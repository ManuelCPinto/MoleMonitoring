import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
import pandas as pd
from PIL import Image

BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "HAM10000"))
IMAGES_FOLDER = os.path.join(BASE_FOLDER, "HAM10000_images_processed", "rgb")
METADATA_FILE = os.path.join(BASE_FOLDER, "HAM10000_metadata")

TEST_FOLDER = os.path.join(BASE_FOLDER, "ISIC2018_Images_processed", "rgb")
TEST_METADATA = os.path.join(BASE_FOLDER, "ISIC2018_TestSet", "ISIC2018_metadata")

NUM_SAMPLES = 10000
TRAIN_SPLIT = 0.8  
NUM_EPOCHS = 40
BATCH_SIZE = 64
NUM_CLASSES = None

metadata = pd.read_csv(METADATA_FILE)
test_metadata = pd.read_csv(TEST_METADATA)

if NUM_SAMPLES < len(metadata):
    metadata = metadata.sample(n=NUM_SAMPLES, random_state=42).reset_index(drop=True)

lesion_classes = {name: idx for idx, name in enumerate(metadata["dx"].unique())}
metadata["label"] = metadata["dx"].map(lesion_classes)
test_metadata["label"] = test_metadata["dx"].map(lesion_classes)

NUM_CLASSES = len(lesion_classes)

class SkinLesionDataset(Dataset):
    def __init__(self, metadata, images_folder, transform=None):
        self.metadata = metadata
        self.images_folder = images_folder
        self.transform = transform

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        img_path = os.path.join(self.images_folder, row["image_id"] + ".jpg")
        label = row["label"]
        
        if not os.path.exists(img_path):
            print(f"Warning: {img_path} not found. Skipping...")
            return self.__getitem__((idx + 1) % len(self.metadata))
    
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.long)

transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

full_dataset = SkinLesionDataset(metadata, IMAGES_FOLDER, transform=transform)

test_dataset = SkinLesionDataset(test_metadata, TEST_FOLDER, transform=test_transform)

train_size = int(TRAIN_SPLIT * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

class SkinLesionCNN(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES):
        super(SkinLesionCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(128 * 32 * 32, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, num_classes)
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 128 * 32 * 32)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
model = SkinLesionCNN(num_classes=NUM_CLASSES).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def train_model(model, train_loader, val_loader, criterion, optimizer, epochs=10):
    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []
    
    for epoch in range(epochs):
        model.train()
        train_loss, correct, total = 0.0, 0, 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
        
        train_acc = correct / total
        val_loss, val_acc = evaluate_runtime(model, val_loader, criterion)
        
        train_losses.append(train_loss / len(train_loader.dataset))
        val_losses.append(val_loss)
        train_accuracies.append(train_acc)
        val_accuracies.append(val_acc)
        
        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss/len(train_loader.dataset):.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
    
    # Plot training and validation loss
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(1, epochs+1), train_losses, label='Train Loss')
    plt.plot(range(1, epochs+1), val_losses, label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Loss Evolution')
    plt.legend()
    
    # Plot training and validation accuracy
    plt.subplot(1, 2, 2)
    plt.plot(range(1, epochs+1), train_accuracies, label='Train Accuracy')
    plt.plot(range(1, epochs+1), val_accuracies, label='Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.title('Accuracy Evolution')
    plt.legend()
    
    plt.show()

def evaluate_runtime(model, loader, criterion):
    model.eval()
    loss, correct, total = 0.0, 0, 0
    y_true, y_pred = [], []
    
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss += criterion(outputs, labels).item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            y_true.extend(labels.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())
    
    print(classification_report(y_true, y_pred, target_names=lesion_classes.keys()))
    return loss / len(loader.dataset), correct / total

def evaluate_test_model(model, loader, criterion):
    model.eval()
    loss, correct, total = 0.0, 0, 0
    y_true, y_pred = [], []
    
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss += criterion(outputs, labels).item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            y_true.extend(labels.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())
    
    print(classification_report(y_true, y_pred, target_names=lesion_classes.keys()))
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=lesion_classes.keys(), yticklabels=lesion_classes.keys())
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()
    return loss / len(loader.dataset), correct / total

train_model(model, train_loader, val_loader, criterion, optimizer, epochs=NUM_EPOCHS)

test_loss, test_acc = evaluate_test_model(model, test_loader, criterion)
print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_acc:.4f}")