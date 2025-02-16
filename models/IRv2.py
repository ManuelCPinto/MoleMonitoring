import os
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import timm
from sklearn.preprocessing import label_binarize

# ---------------------------
# Dataset Class (global scope)
# ---------------------------
class SkinLesionDataset(Dataset):
    def __init__(self, df, folder, label_map, transform, oversample_targets=None, is_test=False):
        self.label_map = label_map
        self.folder = folder
        self.transform = transform
        self.is_test = is_test
        self.df = df

        if oversample_targets and not is_test:
            print("Oversampling data for classes ...")
            grp = df.groupby("dx")
            balanced_df = []
            for dx, group in grp:
                target_num = oversample_targets.get(dx, len(group))
                mult = max(1, target_num // len(group))
                balanced_df.append(pd.DataFrame(np.repeat(group.values, mult, axis=0), columns=group.columns))
            self.df = pd.concat(balanced_df).reset_index(drop=True)
            print(f"After oversampling, total samples: {len(self.df)}")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        lbl = self.label_map[row["dx"]]
        path = os.path.join(self.folder, f"{row['image_id']}.jpg")
        img = np.array(Image.open(path).convert("RGB"))
        augmented = self.transform(image=img)
        image_tensor = augmented["image"].float()
        return image_tensor, torch.tensor(lbl, dtype=torch.long)

# ---------------------------
# Soft Attention Module
# ---------------------------
class SoftAttention(nn.Module):
    def __init__(self, channels, heads, aggregate=True, concat_with_x=False):
        super(SoftAttention, self).__init__()
        self.channels = channels
        self.multiheads = heads
        self.aggregate_channels = aggregate
        self.concat_input_with_scaled = concat_with_x
        self.conv = nn.Conv3d(1, heads, kernel_size=(channels, 3, 3), padding=(0, 1, 1), bias=True)

    def forward(self, x):
        b, c, h, w = x.shape
        x_exp = x.unsqueeze(1) 
        conv3d = self.conv(x_exp).squeeze(2) 
        attn_maps = F.softmax(conv3d.view(b, self.multiheads, -1), dim=-1).view(b, self.multiheads, h, w)
        if self.aggregate_channels:
            attn_maps = attn_maps.sum(dim=1, keepdim=True)
            x_out = x * attn_maps
        else:
            x_out = x * attn_maps.unsqueeze(1)
        if self.concat_input_with_scaled:
            return torch.cat([x_out, x], dim=1)
        return x_out

# ---------------------------
# Model Definition: InceptionResNetV2 with Soft Attention
# ---------------------------
class InceptionResNetV2_SoftAttention(nn.Module):
    def __init__(self, num_classes, dropout_p):
        super(InceptionResNetV2_SoftAttention, self).__init__()
        self.num_classes = num_classes 
        print("Creating base model (this may download weights if not cached)...")
        self.base_model = timm.create_model("inception_resnet_v2", pretrained=True, num_classes=0, global_pool="")
        print("Base model created.")
        self.soft_attention = SoftAttention(1536, heads=16, aggregate=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_p)
        self.fc = None 

    def forward(self, x):
        features = self.base_model.forward_features(x) 
        attn_features = self.soft_attention(features)
        pooled_features = self.pool(features)
        pooled_attn = self.pool(attn_features)
        combined = torch.cat([pooled_features, pooled_attn], dim=1)
        activated = self.relu(combined)
        dropped = self.dropout(activated)
        flat = torch.flatten(dropped, 1)
        if self.fc is None:
            self.fc = nn.Linear(flat.shape[1], self.num_classes).to(flat.device)
        out = self.fc(flat)
        return out

# ---------------------------
# Main Function
# ---------------------------
def main():
    print("Starting main function...")
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    HAM_FOLDER = os.path.join(BASE_PATH, "HAM10000")
    HAM_IMAGES_FOLDER = os.path.join(HAM_FOLDER, "HAM10000_images")
    HAM_METADATA_FILE = os.path.join(HAM_FOLDER, "HAM10000_metadata")

    ISIC_FOLDER = os.path.join(BASE_PATH, "ISIC2018")
    ISIC_IMAGES_FOLDER = os.path.join(ISIC_FOLDER, "ISIC2018_images")
    ISIC_METADATA_FILE = os.path.join(ISIC_FOLDER, "ISIC2018_metadata")

    CHECKPOINT_PATH = "best_inception_resnetv2_attention.pth"

    NUM_EPOCHS = 100
    BATCH_SIZE = 64
    LR = 1e-4
    DROPOUT_P = 0.5
    PATIENCE = 15
    IMG_SIZE = 299  

    ham_classes = ["nv", "mel", "bkl", "bcc", "akiec", "vasc", "df"]
    label_map = {name: idx for idx, name in enumerate(ham_classes)}
    NUM_CLASSES = len(ham_classes)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)

    if device == 'cuda':
        torch.backends.cudnn.benchmark = True

    # ---------------------------
    # Augmentation Transforms
    # ---------------------------
    print("Setting up augmentation transforms...")
    train_transform = A.Compose([
        A.RandomResizedCrop(
            size=(IMG_SIZE, IMG_SIZE),
            scale=(0.8, 1.0),
            ratio=(0.9, 1.1),
            interpolation=cv2.INTER_CUBIC,
            p=1.0
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Rotate(limit=180, p=0.5),
        A.Affine(
            scale=(0.9, 1.1),
            translate_percent=(-0.1, 0.1),
            rotate=(-30, 30),
            p=0.5
        ),
        A.RGBShift(r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, p=0.5),
        A.RandomBrightnessContrast(p=0.5),
        A.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
        ToTensorV2()
    ])

    test_transform = A.Compose([
        A.Resize(height=IMG_SIZE, width=IMG_SIZE),
        A.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
        ToTensorV2()
    ])
    print("Transforms set up.")

    oversample_targets = {
        "mel": 2000,
        "akiec": 1800,
        "bcc": 1500,
        "bkl": 1300,
        "df": 1000,
        "vasc": 1000
    }

    # ---------------------------
    # Data Loading and DataLoaders
    # ---------------------------
    print("Reading HAM metadata file...")
    HAM = pd.read_csv(HAM_METADATA_FILE)
    print("Creating training/validation split...")
    train_df, val_df = train_test_split(HAM, test_size=0.1, stratify=HAM["dx"], random_state=42)
    print(f"Training samples: {len(train_df)}, Validation samples: {len(val_df)}")

    print("Creating training and validation datasets...")
    train_dataset = SkinLesionDataset(train_df, HAM_IMAGES_FOLDER, label_map, train_transform, oversample_targets)
    val_dataset = SkinLesionDataset(val_df, HAM_IMAGES_FOLDER, label_map, test_transform, is_test=True)
    print("Datasets created.")

    # Set num_workers, persistent_workers, and prefetch_factor in DataLoaders
    num_workers = os.cpu_count() - 2 if os.cpu_count() and os.cpu_count() > 2 else 0

    print("Creating DataLoaders...")
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=num_workers, pin_memory=True,
                              persistent_workers=True, prefetch_factor=2)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=num_workers, pin_memory=True,
                            persistent_workers=True, prefetch_factor=2)
    print("Training and validation DataLoaders created.")

    print("Reading ISIC metadata file and creating test DataLoader...")
    ISIC = pd.read_csv(ISIC_METADATA_FILE)
    test_dataset = SkinLesionDataset(ISIC, ISIC_IMAGES_FOLDER, label_map, test_transform, is_test=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=num_workers, pin_memory=True,
                             persistent_workers=True, prefetch_factor=2)
    print("Test DataLoader created.")

    # ---------------------------
    # Model, Loss, Optimizer, and GradScaler Setup
    # ---------------------------
    print("Creating model...")
    model = InceptionResNetV2_SoftAttention(num_classes=NUM_CLASSES, dropout_p=DROPOUT_P).to(device)
    print("Model created.")
    class_weights = torch.tensor([1.0, 1.0, 1.0, 1.0, 5.0, 1.0, 1.0]).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    scaler = torch.amp.GradScaler("cuda") if device == 'cuda' else None

    best_val_acc = 0.0
    patience_counter = 0

    # ---------------------------
    # Training Loop
    # ---------------------------
    print("Starting training loop...")
    for epoch in range(NUM_EPOCHS):
        start_time = time.time()
        model.train()
        running_loss, running_correct, total = 0.0, 0, 0

        for images, labels in train_loader:
            images = images.to(device, memory_format=torch.channels_last)
            labels = labels.to(device)
            optimizer.zero_grad()

            with torch.amp.autocast(device_type='cuda', enabled=(scaler is not None)):
                outputs = model(images)
                loss = criterion(outputs, labels)

            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            running_loss += loss.item() * images.size(0)
            running_correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_acc  = running_correct / total

        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad(), torch.amp.autocast(device_type='cuda', enabled=(scaler is not None)):
            for images, labels in val_loader:
                images = images.to(device, memory_format=torch.channels_last)
                labels = labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                val_correct += (outputs.argmax(dim=1) == labels).sum().item()
                val_total += labels.size(0)

        val_loss /= val_total
        val_acc = val_correct / val_total
        epoch_time = time.time() - start_time

        print(f"Epoch [{epoch+1}/{NUM_EPOCHS}] -> Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, Time: {epoch_time:.2f} sec")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), CHECKPOINT_PATH)
            print("New best model saved!")
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print("Early stopping triggered!")
                break

    print("Training finished. Loading best model...")
    model.load_state_dict(torch.load(CHECKPOINT_PATH))
    model.eval()

    # ---------------------------
    # Evaluation Function
    # ---------------------------
    def evaluate_model():
        y_true, y_pred, y_prob = [], [], []
        print("Starting evaluation on test data...")
        model.eval()
        with torch.no_grad(), torch.amp.autocast(device_type='cuda', enabled=(scaler is not None)):
            for images, labels in test_loader:
                images = images.to(device, memory_format=torch.channels_last)
                labels = labels.to(device)
                outputs = model(images)
                probs = F.softmax(outputs, dim=1)
                preds = outputs.argmax(dim=1)
                y_true.extend(labels.cpu().numpy())
                y_pred.extend(preds.cpu().numpy())
                y_prob.extend(probs.cpu().numpy())

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        y_prob = np.array(y_prob)

        print("\n**Classification Report on ISIC2018 Test Data:**")
        print(classification_report(y_true, y_pred, target_names=ham_classes))

        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=ham_classes, yticklabels=ham_classes)
        plt.title("Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.show()

        y_true_bin = label_binarize(y_true, classes=list(range(NUM_CLASSES)))
        fpr = {}
        tpr = {}
        roc_auc = {}
        for i in range(NUM_CLASSES):
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
            plt.plot(fpr[i], tpr[i], label=f"{ham_classes[i]} (AUC = {roc_auc[i]:.2f})")
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([-0.1, 1.1])
        plt.ylim([-0.1, 1.1])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curves")
        plt.legend(loc="lower right")
        plt.show()
        print("Evaluation finished.")

    evaluate_model()

if __name__ == '__main__':
    main()
