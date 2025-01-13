import os
import zipfile
import shutil

base_path = os.path.dirname(os.path.abspath(__file__))
zip_file = os.path.join(base_path, "dataverse_files.zip")
output_folder = os.path.join(base_path, "dataverse_files")
ham_folder = os.path.join(base_path, "HAM10000")
images_folder = os.path.join(ham_folder, "HAM10000_images")

print("Extracting dataverse_files.zip...")
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(output_folder)

os.makedirs(images_folder, exist_ok=True)

def extract_images(zip_path, target_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)

ham_zip_1 = os.path.join(output_folder, "HAM10000_images_part_1.zip")
ham_zip_2 = os.path.join(output_folder, "HAM10000_images_part_2.zip")

print("Extracting HAM10000 images...")
extract_images(ham_zip_1, images_folder)
extract_images(ham_zip_2, images_folder)

metadata_file = os.path.join(output_folder, "HAM10000_metadata")
if os.path.exists(metadata_file):
    shutil.move(metadata_file, os.path.join(ham_folder, "HAM10000_metadata"))

print("Removing unnecessary files and folders...")
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

if os.path.exists(zip_file):
    os.remove(zip_file)

print("Merge complete!")
