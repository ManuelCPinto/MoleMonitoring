import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision.models import resnet50
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2

# ---------------------------
# Define Paths
# ---------------------------
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HAM_FOLDER = os.path.join(BASE_PATH, "HAM10000")
HAM_IMAGES_FOLDER = os.path.join(HAM_FOLDER, "HAM10000_images")
HAM_METADATA_FILE = os.path.join(HAM_FOLDER, "HAM10000_metadata")

ISIC_FOLDER = os.path.join(BASE_PATH, "ISIC2018")
ISIC_IMAGES_FOLDER = os.path.join(ISIC_FOLDER, "ISIC2018_images")
ISIC_METADATA_FILE = os.path.join(ISIC_FOLDER, "ISIC2018_metadata")

CHECKPOINT_PATH = "best_model.pth" 

# ---------------------------
# Hyperparameters
# ---------------------------
NUM_EPOCHS = 150
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
DROPOUT_P = 0.3
PATIENCE = 30
TARGET_SAMPLES_PER_CLASS = 4000  # Oversampling + Augmentation limit

# ---------------------------
# Augmentation Strategy
# ---------------------------
train_transform = A.Compose([
    A.HorizontalFlip(),
    A.VerticalFlip(),
    A.RandomRotate90(),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=180, p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.HueSaturationValue(p=0.2),
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

test_transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

# ---------------------------
# Custom Dataset with Oversampling & Augmentation
# ---------------------------
class SkinLesionDataset(Dataset):
    def __init__(self, metadata, images_folder, label_map, transform=None, oversample_target=None):
        self.metadata = metadata
        self.images_folder = images_folder
        self.label_map = label_map
        self.transform = transform

        self.augmented_data = []
        class_counts = self.metadata["dx"].value_counts().to_dict()

        for cls, count in class_counts.items():
            class_data = self.metadata[self.metadata["dx"] == cls]
            multiplier = max(1, min(TARGET_SAMPLES_PER_CLASS // count, 10)) 
            self.augmented_data.extend([row for _, row in class_data.iterrows()] * multiplier)
        
        self.augmented_data = pd.DataFrame(self.augmented_data).reset_index(drop=True)

    def __len__(self):
        return len(self.augmented_data)

    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        img_id = row["image_id"]
        dx = row["dx"]
        label = self.label_map[dx]

        img_path = os.path.join(self.images_folder, f"{img_id}.jpg")
        image = Image.open(img_path).convert("RGB")
        image = np.array(image)

        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]

        return image.float(), torch.tensor(label, dtype=torch.long)

# ---------------------------
# Load & Prepare Datasets
# ---------------------------
ham_metadata = pd.read_csv(HAM_METADATA_FILE)
ham_classes = sorted(ham_metadata["dx"].unique())
label_map = {name: idx for idx, name in enumerate(ham_classes)}
NUM_CLASSES = len(label_map)

# Train/Validation Split (90% Train / 10% Validation)
train_df, val_df = train_test_split(ham_metadata, test_size=0.10, stratify=ham_metadata["dx"])

# Compute Class Weights
class_counts = train_df["dx"].value_counts().to_dict()
total_samples = sum(class_counts.values())
class_weights = {label_map[cls]: total_samples / (len(class_counts) * count) for cls, count in class_counts.items()}
class_weights_tensor = torch.tensor(list(class_weights.values()), dtype=torch.float).to("cuda")

train_dataset = SkinLesionDataset(train_df, HAM_IMAGES_FOLDER, label_map, transform=train_transform, oversample_target=TARGET_SAMPLES_PER_CLASS)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

val_dataset = SkinLesionDataset(val_df, HAM_IMAGES_FOLDER, label_map, transform=test_transform)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

isic_metadata = pd.read_csv(ISIC_METADATA_FILE)
test_dataset = SkinLesionDataset(isic_metadata, ISIC_IMAGES_FOLDER, label_map, transform=test_transform)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ---------------------------
# Load Pretrained ResNet50 & Modify
# ---------------------------
resnet = resnet50(weights="IMAGENET1K_V1")
modules = list(resnet.children())[:-2]
resnet = nn.Sequential(*modules)

conv = nn.Sequential(
    nn.AdaptiveAvgPool2d((1, 1)),
    nn.Flatten(),
    nn.Dropout(p=DROPOUT_P),
    nn.Linear(2048, NUM_CLASSES)
)

model = nn.Sequential(resnet, conv).to("cuda")

optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE)
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

# ---------------------------
# Training with Checkpointing
# ---------------------------
best_val_acc = 0
patience_counter = 0

for epoch in range(NUM_EPOCHS):
    model.train()
    train_loss, correct, total = 0.0, 0, 0
    for images, labels in train_loader:
        images, labels = images.to("cuda"), labels.to("cuda")
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    train_acc = correct / total
    train_loss /= len(train_loader)

    model.eval()
    val_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to("cuda"), labels.to("cuda")
            outputs = model(images)
            val_loss += criterion(outputs, labels).item()
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

    val_acc = correct / total
    val_loss /= len(val_loader)

    print(f"Epoch [{epoch+1}/{NUM_EPOCHS}] -> Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

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

model.load_state_dict(torch.load(CHECKPOINT_PATH))
model.eval()

# ---------------------------
# Evaluation Function
# ---------------------------
def evaluate_model():
    y_true, y_pred = [], []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to("cuda"), labels.to("cuda")
            outputs = model(images)
            preds = outputs.argmax(dim=1)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())

    print("\n**Classification Report on ISIC2018:**")
    print(classification_report(y_true, y_pred, target_names=ham_classes))

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=ham_classes, yticklabels=ham_classes)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.show()

evaluate_model()

y_true, y_pred = [], []

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to("cuda"), labels.to("cuda")
        outputs = model(images)
        preds = outputs.argmax(dim=1)

        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())

print("\n**Classification Report on ISIC2018:**")
print(classification_report(y_true, y_pred, target_names=ham_classes))
