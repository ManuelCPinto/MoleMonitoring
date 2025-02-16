import torch
import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch.optim as optim

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

# from torch.utils.tensorboard import SummaryWriter
sys.setrecursionlimit(15000)

from PIL import Image
from torch.optim import lr_scheduler
from torch.autograd import Variable
from torch.utils.data import DataLoader, Dataset
import seaborn as sns
import albumentations as A
from albumentations.pytorch import ToTensorV2
from tqdm.notebook import tqdm

from FixCaps_model import FixCapsNet

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

CHECKPOINT_PATH = "best_model_fixcaps.pth"

# ---------------------------
# Hyperparameters
# ---------------------------
NUM_EPOCHS = 120
BATCH_SIZE = 256
PATIENCE = 40
TARGET_SAMPLES_PER_CLASS = 4000 

n_channels = 3
conv_outputs = 128
num_primary_units = 8
primary_unit_size = 16 * 6 * 6
output_unit_size = 16
mode='128'
n_classes = 7

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
    def __init__(self, metadata, images_folder, label_map, transform=None, oversample_target=None, oversample=True):
        self.metadata = metadata
        self.images_folder = images_folder
        self.label_map = label_map
        self.transform = transform

        if oversample:
            self.augmented_data = []
            class_counts = self.metadata["dx"].value_counts().to_dict()
    
            for cls, count in class_counts.items():
                class_data = self.metadata[self.metadata["dx"] == cls]
                multiplier = max(1, min(TARGET_SAMPLES_PER_CLASS // count, 10)) 
                self.augmented_data.extend([row for _, row in class_data.iterrows()] * multiplier)
    
            self.augmented_data = pd.DataFrame(self.augmented_data).reset_index(drop=True)
        else:
            # No oversampling for test dataset
            self.augmented_data = self.metadata.copy()

    def __len__(self):
        return len(self.augmented_data)

    def __getitem__(self, idx):
        row = self.augmented_data.iloc[idx]
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

train_df, val_df = train_test_split(ham_metadata, test_size=0.10, stratify=ham_metadata["dx"])

class_counts = train_df["dx"].value_counts().to_dict()
total_samples = sum(class_counts.values())
class_weights = {label_map[cls]: total_samples / (len(class_counts) * count) for cls, count in class_counts.items()}
class_weights_tensor = torch.tensor(list(class_weights.values()), dtype=torch.float).to("cuda")

train_dataset = SkinLesionDataset(train_df, HAM_IMAGES_FOLDER, label_map, transform=train_transform, oversample_target=TARGET_SAMPLES_PER_CLASS)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

val_dataset = SkinLesionDataset(val_df, HAM_IMAGES_FOLDER, label_map, transform=test_transform)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

isic_metadata = pd.read_csv(ISIC_METADATA_FILE)
test_dataset = SkinLesionDataset(isic_metadata, ISIC_IMAGES_FOLDER, label_map, transform=test_transform, oversample=False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ---------------------------
# Create Capsule Network
# ---------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

model = FixCapsNet(conv_inputs=n_channels,
                     conv_outputs=conv_outputs,
                     primary_units=num_primary_units,
                     primary_unit_size=primary_unit_size,
                     num_classes=n_classes,
                     output_unit_size=16,
                     init_weights=True,
                     mode=mode)
model = model.to(device)

# ---------------------------
# Training with Checkpointing
# ---------------------------

def one_hot(x, length):
    batch_size = x.size(0)
    x_one_hot = torch.zeros(batch_size, length)
    for i in range(batch_size):
        x_one_hot[i, x[i]] = 1.0
    return x_one_hot

learning_rate = 0.123
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
scheduler = lr_scheduler.CosineAnnealingLR(optimizer, 5, eta_min=1e-8, last_epoch=-1)

best_train = 0.0
train_evl_result = None

def train_one_epoch(epoch):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    train_tmp_result = torch.zeros(n_classes, n_classes)
    
    for data, target in train_loader:
        target_indices = target.clone()
        target_one_hot = one_hot(target, length=n_classes)
        data, target = Variable(data).to(device), Variable(target_one_hot).to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = model.loss(output, target, size_average=True)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        v_mag = torch.sqrt(torch.sum(output**2, dim=2, keepdim=True)) 
        pred = v_mag.data.max(1, keepdim=True)[1].cpu().squeeze()
        correct += pred.eq(target_indices.view_as(pred)).sum().item()
        total += target_indices.size(0)
        
        for i in range(target_indices.size(0)):
            train_tmp_result[target_indices[i]][pred[i].numpy()] += 1
    
    epoch_acc = correct / total
    epoch_loss = running_loss / len(train_loader)
    scheduler.step()
    
    return epoch_loss, epoch_acc, train_tmp_result

def validate():
    model.eval()
    val_loss, correct, total = 0.0, 0, 0
    
    with torch.no_grad():
        for data, target in val_loader:
            target_indices = target.clone()
            target_one_hot = one_hot(target, length=n_classes)
            data, target = Variable(data).to(device), Variable(target_one_hot).to(device)
            
            output = model(data)
            loss = model.loss(output, target, size_average=True)
            val_loss += loss.item()
            
            v_mag = torch.sqrt(torch.sum(output**2, dim=2, keepdim=True)) 
            pred = v_mag.data.max(1, keepdim=True)[1].cpu().squeeze()
            correct += pred.eq(target_indices.view_as(pred)).sum().item()
            total += target_indices.size(0)
    
    val_acc = correct / total
    val_loss /= len(val_loader)
    
    return val_loss, val_acc

best_val_acc = 0.0
patience_counter = 0

train_losses, val_losses, train_accs, val_accs = [], [], [], []

for epoch in range(1, NUM_EPOCHS + 1):
    train_loss, train_acc, train_tmp_result = train_one_epoch(epoch)
    val_loss, val_acc = validate()
    
    train_losses.append(train_loss)
    val_losses.append(val_loss)
    train_accs.append(train_acc)
    val_accs.append(val_acc)
    
    print(f"Epoch [{epoch}/{NUM_EPOCHS}] -> Train Loss: {train_loss:.5f}, Train Acc: {train_acc:.5f}, Val Loss: {val_loss:.5f}, Val Acc: {val_acc:.5f}")
    
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        patience_counter = 0
        best_train = train_acc
        train_evl_result = train_tmp_result.clone()
        torch.save(model.state_dict(), CHECKPOINT_PATH)
        print("New best model saved!")
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            print("Early stopping triggered!")
            break

model.load_state_dict(torch.load(CHECKPOINT_PATH))
model.eval()

# Plot training and validation loss
plt.figure(figsize=(10,5))
plt.plot(range(1, len(train_losses)+1), train_losses, label='Train Loss')
plt.plot(range(1, len(val_losses)+1), val_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.show()

# Plot training and validation accuracy
plt.figure(figsize=(10,5))
plt.plot(range(1, len(train_accs)+1), train_accs, label='Train Accuracy')
plt.plot(range(1, len(val_accs)+1), val_accs, label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()
plt.show()


# ---------------------------
# Evaluation Function
# ---------------------------
def evaluate_model():
    model.eval()

    all_targets = []
    all_preds = []

    with torch.no_grad():
        for data, target in tqdm(test_loader):
            target_indices = target.clone()
            target_one_hot = one_hot(target, length=n_classes)
            data, target = Variable(data).to(device), Variable(target_one_hot).to(device)

            output = model(data)
            v_mag = torch.sqrt(torch.sum(output**2, dim=2, keepdim=True))
            pred = v_mag.data.max(1, keepdim=True)[1].cpu().squeeze()

            all_targets.extend(target_indices.cpu().numpy())
            all_preds.extend(pred.numpy())

    # Compute the confusion matrix
    cm = confusion_matrix(all_targets, all_preds)

    # Get class labels
    class_labels = list(label_map.keys())

    # Plot the confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_labels, yticklabels=class_labels)
    plt.xlabel("Predicted Labels")
    plt.ylabel("True Labels")
    plt.title("Confusion Matrix (Test Data)")
    plt.show()
    
    print("\n**Classification Report on ISIC2018:**")
    print(classification_report(all_targets, all_preds, target_names=ham_classes))

# Call the function
evaluate_model()

