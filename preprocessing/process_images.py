import os
import tensorflow as tf

base_folder = "../HAM10000"
images_folder = os.path.join(base_folder, "HAM10000_images")
processed_folder = os.path.join(base_folder, "HAM10000_images_processed") 

target_size = (256, 256)

os.makedirs(processed_folder, exist_ok=True)

def resize_images(input_folder, target_size):
    print("Resizing images in HAM10000_images folder...")
    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = tf.io.read_file(img_path)
            img = tf.image.decode_image(img, channels=3)
            resized_img = tf.image.resize(img, target_size)
            resized_img = tf.cast(resized_img, tf.uint8)
            tf.keras.preprocessing.image.save_img(img_path, resized_img)

    print("All images resized to 256x256 and overwritten in 'HAM10000_images'.")
    
def normalize_images(input_folder, output_folder, target_size):
    print("Normalizing images and saving to HAM10000_images_processed folder...")
    
    rgb_folder = os.path.join(output_folder, "rgb")
    grayscale_folder = os.path.join(output_folder, "grayscale")
    
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(grayscale_folder, exist_ok=True)
    
    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = tf.io.read_file(img_path)
            img = tf.image.decode_image(img, channels=3)

            resized_img = tf.image.resize(img, target_size)

            normalized_rgb = resized_img / 255.0

            grayscale_img = tf.image.rgb_to_grayscale(resized_img)
            normalized_grayscale = grayscale_img / 255.0

            rgb_output_path = os.path.join(rgb_folder, img_file)
            tf.keras.preprocessing.image.save_img(rgb_output_path, normalized_rgb)

            grayscale_output_path = os.path.join(grayscale_folder, img_file)
            tf.keras.preprocessing.image.save_img(grayscale_output_path, normalized_grayscale)

    print("All images normalized (RGB and grayscale) and saved to 'HAM10000_images_processed'.")


resize_images(images_folder, target_size)

normalize_images(images_folder, processed_folder, target_size)
