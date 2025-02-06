import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2
import timm

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

CHECKPOINT_PATH = "best_inception_resnetv2.pth"

# ---------------------------
# Hyperparameters
# ---------------------------
NUM_EPOCHS = 90
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
DROPOUT_P = 0.3
PATIENCE = 10  
TARGET_SAMPLES_PER_CLASS = 4000  

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
    A.Resize(299, 299),  
    A.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
    ToTensorV2(),
])

test_transform = A.Compose([
    A.Resize(299, 299),
    A.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
    ToTensorV2(),
])

# ---------------------------
# Soft Attention Module
# ---------------------------
class SoftAttention(nn.Module):
    def __init__(self, channels, multiheads=8, aggregate=True, concat_with_x=False):
        super(SoftAttention, self).__init__()
        self.multiheads = multiheads
        self.aggregate = aggregate
        self.concat_with_x = concat_with_x
        self.conv3d = nn.Conv3d(in_channels=1, out_channels=multiheads, kernel_size=(3, 3, channels), padding=(1, 1, 0))
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=-1)
    
    def forward(self, x):
        b, c, h, w = x.shape
        x_exp = x.unsqueeze(1) 
        attention_maps = self.conv3d(x_exp).squeeze(-1)
        attention_maps = self.relu(attention_maps)
        attention_maps = self.softmax(attention_maps.view(b, self.multiheads, -1))
        attention_maps = attention_maps.view(b, self.multiheads, h, w)
        
        if self.aggregate:
            attention_maps = attention_maps.sum(dim=1, keepdim=True)
            x = x * attention_maps
        else:
            x = torch.cat([x, x * attention_maps], dim=1)
        
        return x

# ---------------------------
# Custom Dataset with Augmentation
# ---------------------------
class SkinLesionDataset(Dataset):
    def __init__(self, metadata, images_folder, label_map, transform=None):
        self.metadata = metadata
        self.images_folder = images_folder
        self.label_map = label_map
        self.transform = transform

    def __len__(self):
        return len(self.metadata)

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

train_df, val_df = train_test_split(ham_metadata, test_size=0.10, stratify=ham_metadata["dx"])

class_counts = train_df["dx"].value_counts().to_dict()
total_samples = sum(class_counts.values())
class_weights = {label_map[cls]: total_samples / (len(class_counts) * count) for cls, count in class_counts.items()}
class_weights_tensor = torch.tensor(list(class_weights.values()), dtype=torch.float).to("cuda")

train_dataset = SkinLesionDataset(train_df, HAM_IMAGES_FOLDER, label_map, transform=train_transform)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

val_dataset = SkinLesionDataset(val_df, HAM_IMAGES_FOLDER, label_map, transform=test_transform)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

isic_metadata = pd.read_csv(ISIC_METADATA_FILE)
test_dataset = SkinLesionDataset(isic_metadata, ISIC_IMAGES_FOLDER, label_map, transform=test_transform)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ---------------------------
# Load Pretrained Inception-ResNet-v2 with Soft Attention
# ---------------------------
model = timm.create_model("inception_resnet_v2", pretrained=True, num_classes=NUM_CLASSES)
model.global_pool = SoftAttention(channels=1536)
model.to("cuda")

optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

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
