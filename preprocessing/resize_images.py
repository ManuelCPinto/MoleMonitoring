import os
import tensorflow as tf

base_folder = "../HAM10000" 
images_folder = os.path.join(base_folder, "HAM10000_images")
processed_folder = os.path.join(base_folder, "HAM10000_images_processed")

target_size = (256, 256)

os.makedirs(processed_folder, exist_ok=True)

def resize_images(input_folder, output_folder, target_size):
    print("Resizing images...")
    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = tf.io.read_file(img_path)
            img = tf.image.decode_image(img, channels=3) 

            resized_img = tf.image.resize(img, target_size)

            resized_img = tf.cast(resized_img, tf.uint8)

            output_path = os.path.join(output_folder, img_file)
            tf.keras.preprocessing.image.save_img(output_path, resized_img)

resize_images(images_folder, processed_folder, target_size)
print("All images resized to 256x256 and stored in 'HAM10000_images_processed'.")
