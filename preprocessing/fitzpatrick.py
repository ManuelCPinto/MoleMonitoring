import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

base_folder = "../HAM10000"
images_folder = os.path.join(base_folder, "HAM10000_images_processed", "rgb")
segmentations_folder = os.path.join(base_folder, "HAM10000_segmentations_processed")
metadata_file = os.path.join(base_folder, "HAM10000_metadata")
plots_folder = os.path.join(base_folder, "plots")

os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv(metadata_file)

def extract_skin_tone(image_path, mask_path, image_id):
    img = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) 

    _, binary_mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)

    skin_mask = cv2.bitwise_not(binary_mask)

    skin_pixels = img[skin_mask == 255]

    avg_skin_color = np.mean(skin_pixels, axis=0).astype(int)
    save_visualization(img, mask, skin_mask, image_id)

    return avg_skin_color

def classify_fitzpatrick(rgb_values):
    r, g, b = rgb_values
    intensity = (r + g + b) / 3 

    if intensity > 220:
        return "I (Very Fair)"
    elif intensity > 200:
        return "II (Fair)"
    elif intensity > 180:
        return "III (Medium)"
    elif intensity > 160:
        return "IV (Olive)"
    elif intensity > 120:
        return "V (Brown)"
    else:
        return "VI (Dark Brown/Black)"

def save_visualization(img, mask, skin_mask, image_id):
    fig, axes = plt.subplots(1, 4, figsize=(12, 4))

    axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original Image")

    axes[1].imshow(mask, cmap="gray")
    axes[1].set_title("Segmentation Mask")

    axes[2].imshow(skin_mask, cmap="gray")
    axes[2].set_title("Inverted Mask (Skin Area)")

    img_skin_only = cv2.bitwise_and(img, img, mask=skin_mask)
    axes[3].imshow(cv2.cvtColor(img_skin_only, cv2.COLOR_BGR2RGB))
    axes[3].set_title("Extracted Skin Region")

    for ax in axes:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, f"{image_id}_processing.png"))
    plt.close()

fitzpatrick_column = []
print("Classifying images into Fitzpatrick skin types...")

for idx, row in metadata.iterrows():
    image_id = row["image_id"]
    img_file = os.path.join(images_folder, image_id + ".jpg")

    mask_file = os.path.join(segmentations_folder, image_id + "_segmentation.png")

    skin_rgb = extract_skin_tone(img_file, mask_file, image_id)
    fitzpatrick_type = classify_fitzpatrick(skin_rgb)
    fitzpatrick_column.append(fitzpatrick_type)
    
metadata["fitzpatrick_scale"] = fitzpatrick_column

metadata.to_csv(metadata_file, index=False)
print(f"Updated metadata saved with Fitzpatrick scale to: {metadata_file}")
print(f"Processing steps saved in {plots_folder}")
