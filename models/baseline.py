import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
import pandas as pd
from PIL import Image

BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "HAM10000"))
IMAGES_FOLDER = os.path.join(BASE_FOLDER, "HAM10000_images_processed", "rgb")
METADATA_FILE = os.path.join(BASE_FOLDER, "HAM10000_metadata")

NUM_SAMPLES = 1000  
TRAIN_SPLIT = 0.8  
NUM_EPOCHS = 20
BATCH_SIZE = 8
NUM_CLASSES = None

metadata = pd.read_csv(METADATA_FILE)

if NUM_SAMPLES < len(metadata):
    metadata = metadata.sample(n=NUM_SAMPLES, random_state=42).reset_index(drop=True)

lesion_classes = {name: idx for idx, name in enumerate(metadata["dx"].unique())}
metadata["label"] = metadata["dx"].map(lesion_classes)
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

full_dataset = SkinLesionDataset(metadata, IMAGES_FOLDER, transform=transform)

train_size = int(TRAIN_SPLIT * len(full_dataset))
test_size = len(full_dataset) - train_size
train_dataset, test_dataset = random_split(full_dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
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

train_losses, test_losses, test_accuracies = [], [], []

for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    train_losses.append(running_loss / len(train_loader))

    model.eval()
    correct, total, test_loss = 0, 0, 0.0
    y_true, y_pred = [], []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            test_loss += loss.item()

            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())

    test_losses.append(test_loss / len(test_loader))
    test_accuracies.append(correct / total)

    print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {train_losses[-1]:.4f}, "
          f"Test Loss: {test_losses[-1]:.4f}, Accuracy: {test_accuracies[-1]:.4f}")

def evaluate_performance(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=list(lesion_classes.keys()), 
                yticklabels=list(lesion_classes.keys()))
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.plot(range(1, NUM_EPOCHS + 1), train_losses, label="Train Loss", color="blue")
    plt.plot(range(1, NUM_EPOCHS + 1), test_losses, label="Test Loss", color="red")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training & Test Loss")
    plt.legend()
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.plot(range(1, NUM_EPOCHS + 1), test_accuracies, label="Test Accuracy", color="green")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.title("Test Accuracy Over Epochs")
    plt.legend()
    plt.show()

evaluate_performance(y_true, y_pred)