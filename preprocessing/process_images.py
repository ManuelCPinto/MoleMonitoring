import os
import tensorflow as tf
import cv2
import numpy as np
import pandas as pd
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

base_folder = "../HAM10000"
images_folder = os.path.join(base_folder, "HAM10000_images")
test_images_folder = os.path.join(base_folder, "ISIC2018_TestSet", "ISIC2018_Images")
segmentations_folder = os.path.join(base_folder, "HAM10000_segmentations")

processed_images_folder = os.path.join(base_folder, "HAM10000_images_processed")
processed_segmentations_folder = os.path.join(base_folder, "HAM10000_segmentations_processed")
processed_test_images_folder = os.path.join(base_folder, "ISIC2018_Images_processed")

target_size = (256, 256)

os.makedirs(processed_images_folder, exist_ok=True)
os.makedirs(processed_segmentations_folder, exist_ok=True)
os.makedirs(processed_test_images_folder, exist_ok=True)

def remove_hair(img):
    gray_scale = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    blackhat = cv2.morphologyEx(gray_scale, cv2.MORPH_BLACKHAT, kernel)
    bhg = cv2.GaussianBlur(blackhat, (3, 3), cv2.BORDER_DEFAULT)
    _, mask = cv2.threshold(bhg, 10, 255, cv2.THRESH_BINARY)
    dst = cv2.inpaint(img, mask, inpaintRadius=6, flags=cv2.INPAINT_TELEA)
    return dst, mask

def calculate_metrics(original, processed):
    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    psnr_value = psnr(original, processed, data_range=255)
    ssim_value = ssim(original, processed, data_range=255)
    
    return psnr_value, ssim_value

def process_images(input_folder, output_folder, target_size):
    print("Processing images, removing hair, and saving to HAM10000_images_processed folder...")
    
    rgb_folder = os.path.join(output_folder, "rgb")
    grayscale_folder = os.path.join(output_folder, "grayscale")
    metrics_folder = os.path.join(output_folder, "metrics")
    
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(grayscale_folder, exist_ok=True)
    os.makedirs(metrics_folder, exist_ok=True)
    
    metrics = []

    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(img_path)

            resized = tf.image.resize(img, target_size)
            resized = tf.cast(resized, tf.uint8).numpy()
            
            resized_clean, mask = remove_hair(resized)

            rgb_output_path = os.path.join(rgb_folder, img_file)
            cv2.imwrite(rgb_output_path, resized_clean)

            grayscale_img = cv2.cvtColor(resized_clean, cv2.COLOR_RGB2GRAY)
            grayscale_output_path = os.path.join(grayscale_folder, img_file)
            cv2.imwrite(grayscale_output_path, grayscale_img)

            psnr_value, ssim_value = calculate_metrics(resized, resized_clean)
            metrics.append({"image": img_file, "PSNR": psnr_value, "SSIM": ssim_value})

    metrics_df = pd.DataFrame(metrics)
    metrics_csv_path = os.path.join(metrics_folder, "hair_removal_metrics.csv")
    metrics_df.to_csv(metrics_csv_path, index=False)
    print("All images processed and saved to 'HAM10000_images_processed'.")
    print(f"Metrics saved to {metrics_csv_path}")
    
    os.makedirs(output_folder, exist_ok=True)

    for seg_file in os.listdir(input_folder):
        seg_path = os.path.join(input_folder, seg_file)

        if seg_file.lower().endswith('.png'): 
            seg = cv2.imread(seg_path, cv2.IMREAD_GRAYSCALE)
            resized_seg = tf.image.resize(seg[..., np.newaxis], target_size)
            resized_seg = tf.cast(resized_seg, tf.uint8).numpy().squeeze()

            output_path = os.path.join(output_folder, seg_file)
            cv2.imwrite(output_path, resized_seg)

    print(f"All segmentation masks processed and saved to '{output_folder}'.")

process_images(images_folder, processed_images_folder, target_size)
process_images(test_images_folder, processed_test_images_folder, target_size)