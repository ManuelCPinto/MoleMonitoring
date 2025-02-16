import os
# Disable Albumentations update check
os.environ['NO_ALBUMENTATIONS_UPDATE'] = '1'

import time
from datetime import datetime
import base64
import io
import torch
import torch.nn as nn
import torch.nn.functional as F
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import timm

app = Flask(__name__)

# ============================================================
# 1. Model Components
# ============================================================

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

class InceptionResNetV2_SoftAttention(nn.Module):
    def __init__(self, num_classes, dropout_p):
        super(InceptionResNetV2_SoftAttention, self).__init__()
        self.num_classes = num_classes 
        self.base_model = timm.create_model("inception_resnet_v2", pretrained=True, num_classes=0, global_pool="")
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

# ============================================================
# 2. Global Settings and Preprocessing
# ============================================================

IMG_SIZE = 299
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 7
LABELS = ["nv", "mel", "bkl", "bcc", "akiec", "vasc", "df"]

test_transform = A.Compose([
    A.Resize(height=IMG_SIZE, width=IMG_SIZE),
    A.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
    ToTensorV2()
])

# ============================================================
# 3. Load Model and Weights
# ============================================================

model_checkpoint = "best_inception_resnetv2_attention.pth"

model = InceptionResNetV2_SoftAttention(num_classes=NUM_CLASSES, dropout_p=0.5)
model.to(DEVICE)
dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
_ = model(dummy_input)
try:
    # Use weights_only=True for secure loading
    model.load_state_dict(torch.load(model_checkpoint, map_location=DEVICE, weights_only=True))
except Exception as e:
    raise RuntimeError(f"Failed to load model checkpoint: {e}")
model.eval()

# ============================================================
# 4. Formatting Functions
# ============================================================

def format_percentage(prob):
    percent = round(prob * 100, 1)
    if percent < 0.1:
        return "<0.1%"
    if percent.is_integer():
        return f"{int(percent)}%"
    return f"{percent}%"

def format_processing_time(elapsed):
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    return f"{minutes:02d}:{seconds:02d}"

# ============================================================
# 5. Prediction Function
# ============================================================

def predict(image):
    image_np = np.array(image)
    transformed = test_transform(image=image_np)
    image_tensor = transformed["image"].unsqueeze(0).to(DEVICE)
    
    start_time = time.time()
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)
    elapsed_time = time.time() - start_time

    pred_idx = torch.argmax(probs, dim=1).item()
    predicted_label = LABELS[pred_idx]
    confidence_str = format_percentage(probs[0][pred_idx].item())

    detailed_predictions = {
        LABELS[i]: format_percentage(probs[0][i].item())
        for i in range(NUM_CLASSES)
    }
    
    timestamp_str = datetime.utcnow().strftime("%d-%m-%Y - %H:%M:%S")
    processing_time_str = format_processing_time(elapsed_time)
    
    return {
        "timestamp": timestamp_str,
        "prediction": predicted_label,
        "confidence": confidence_str,
        "detailed_predictions": detailed_predictions,
        "processing_time": processing_time_str
    }

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    print(">>> /predict route was hit")
    data = request.get_json()
    print("Payload received:", data)
    
    if not data or 'instances' not in data:
        print("No instances provided in payload.")
        return jsonify({"error": "No instances provided."}), 400

    try:
        base64_image = data['instances'][0]['image']
        print("Base64 image received, length:", len(base64_image))
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        print("Error processing image:", e)
        return jsonify({"error": f"Error processing image: {str(e)}"}), 400

    result = predict(image)
    print("Prediction result:", result)
    
    response = {"predictions": [result]}
    print("Final response:", response)
    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
