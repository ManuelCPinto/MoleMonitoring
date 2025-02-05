import os
import tensorflow as tf
import cv2
import numpy as np
import pandas as pd
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

base_folder = ".."

ham_folder = os.path.join(base_folder, "HAM10000")
images_folder = os.path.join(ham_folder, "HAM10000_images")
segmentations_folder = os.path.join(ham_folder, "HAM10000_segmentations")

processed_images_folder = os.path.join(ham_folder, "HAM10000_images_processed")
processed_segmentations_folder = os.path.join(ham_folder, "HAM10000_segmentations_processed")

isic_folder = os.path.join(base_folder, "ISIC2018")
isic_images_folder = os.path.join(isic_folder, "ISIC2018_images")
processed_isic_images_folder = os.path.join(isic_folder, "ISIC2018_images_processed")

target_size = (256, 256)

os.makedirs(processed_images_folder, exist_ok=True)
os.makedirs(processed_segmentations_folder, exist_ok=True)
os.makedirs(processed_isic_images_folder, exist_ok=True)

def remove_hair(img):
    gray_scale = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    blackhat = cv2.morphologyEx(gray_scale, cv2.MORPH_BLACKHAT, kernel)
    bhg = cv2.GaussianBlur(blackhat, (3, 3), cv2.BORDER_DEFAULT)
    _, mask = cv2.threshold(bhg, 10, 255, cv2.THRESH_BINARY)
    dst = cv2.inpaint(img, mask, inpaintRadius=6, flags=cv2.INPAINT_TELEA)
    return dst, mask

def calculate_metrics(original, processed):
    orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    proc_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    psnr_value = psnr(orig_gray, proc_gray, data_range=255)
    ssim_value = ssim(orig_gray, proc_gray, data_range=255)
    return psnr_value, ssim_value

def process_images(input_folder, output_folder, target_size):
    print(f"Processing images from '{input_folder}' -> '{output_folder}'...")

    rgb_folder = os.path.join(output_folder, "rgb")
    grayscale_folder = os.path.join(output_folder, "grayscale")
    metrics_folder = os.path.join(output_folder, "metrics")

    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(grayscale_folder, exist_ok=True)
    os.makedirs(metrics_folder, exist_ok=True)

    metrics = []

    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        if not img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue

        resized = tf.image.resize(img, target_size)
        resized = tf.cast(resized, tf.uint8).numpy()

        if img_file.lower().endswith('.png'):
            if len(resized.shape) == 3 and resized.shape[2] == 3:
                resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                cleaned_rgb, mask = remove_hair(resized_rgb)
                cleaned_bgr = cv2.cvtColor(cleaned_rgb, cv2.COLOR_RGB2BGR)

                rgb_output_path = os.path.join(rgb_folder, img_file)
                cv2.imwrite(rgb_output_path, cleaned_bgr)

                gray_img = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2GRAY)
                gray_output_path = os.path.join(grayscale_folder, img_file)
                cv2.imwrite(gray_output_path, gray_img)

            
                psnr_val, ssim_val = calculate_metrics(resized, cleaned_bgr)
                metrics.append({"image": img_file, "PSNR": psnr_val, "SSIM": ssim_val})
            else:
                seg_resized = tf.image.resize(resized[..., np.newaxis], target_size)
                seg_resized = tf.cast(seg_resized, tf.uint8).numpy().squeeze()
                seg_out_path = os.path.join(output_folder, img_file)
                cv2.imwrite(seg_out_path, seg_resized)

        else:
            resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            cleaned_rgb, mask = remove_hair(resized_rgb)
            cleaned_bgr = cv2.cvtColor(cleaned_rgb, cv2.COLOR_RGB2BGR)

            rgb_output_path = os.path.join(rgb_folder, img_file)
            cv2.imwrite(rgb_output_path, cleaned_bgr)

            gray_img = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2GRAY)
            gray_output_path = os.path.join(grayscale_folder, img_file)
            cv2.imwrite(gray_output_path, gray_img)

            psnr_val, ssim_val = calculate_metrics(resized, cleaned_bgr)
            metrics.append({"image": img_file, "PSNR": psnr_val, "SSIM": ssim_val})

    metrics_df = pd.DataFrame(metrics)
    metrics_csv_path = os.path.join(metrics_folder, "hair_removal_metrics.csv")
    metrics_df.to_csv(metrics_csv_path, index=False)

    print(f"All images processed and saved to '{output_folder}'.")
    print(f"Metrics saved to {metrics_csv_path}")

process_images(images_folder, processed_images_folder, target_size)
process_images(segmentations_folder, processed_segmentations_folder, target_size)
process_images(isic_images_folder, processed_isic_images_folder, target_size)
