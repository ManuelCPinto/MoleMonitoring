import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
images_folder_rgb = os.path.join(root_folder, "HAM10000", "HAM10000_images_processed", "rgb")
plots_folder = os.path.join(root_folder, "plots")

os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv(metadata_file)

def compute_average_image(group, images_folder):
    group_images = []
    for image_id in group["image_id"]:
        image_path = os.path.join(images_folder, f"{image_id}.jpg")
        if os.path.exists(image_path):
            img = np.array(Image.open(image_path))
            group_images.append(img)
    
    average_image = np.mean(group_images, axis=0)
    return average_image

def save_and_display_image(image, title, output_path):
    plt.figure(figsize=(6, 6))
    plt.imshow(image.astype(np.uint8)) 
    plt.title(title, fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

for category in ["Benign", "Malignant"]:
    group = metadata[metadata["benign_malignant"] == category]
    if not group.empty: 
        average_image_rgb = compute_average_image(group, images_folder_rgb)
        output_path_rgb = os.path.join(plots_folder, f"average_image_{category.lower()}_rgb.png")
        save_and_display_image(average_image_rgb, f"Average Image ({category}, RGB)", output_path_rgb)

class_counts = metadata["dx"].value_counts()
for cls in class_counts.index:
    group = metadata[metadata["dx"] == cls]
    if not group.empty:
        average_image_rgb = compute_average_image(group, images_folder_rgb)
        output_path_rgb = os.path.join(plots_folder, f"average_image_{cls}.png")
        save_and_display_image(average_image_rgb, f"Average Image ({cls}, RGB)", output_path_rgb)
