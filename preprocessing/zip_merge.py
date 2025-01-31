import os
import zipfile
import shutil

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
zip_file = os.path.join(base_path, "dataverse_files.zip")
output_folder = os.path.join(base_path, "dataverse_files")
ham_folder = os.path.join(base_path, "HAM10000")
images_folder = os.path.join(ham_folder, "HAM10000_images")
segmentations_folder = os.path.join(ham_folder, "HAM10000_segmentations")

print("Extracting dataverse_files.zip...")
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(output_folder)

os.makedirs(images_folder, exist_ok=True)
os.makedirs(segmentations_folder, exist_ok=True)

def extract_zip(zip_path, target_folder, remove_subfolder=False):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extract_path = os.path.join(target_folder, "temp_extraction")
        zip_ref.extractall(extract_path)

        for item in os.listdir(extract_path):
            item_path = os.path.join(extract_path, item)
            if os.path.isdir(item_path) and remove_subfolder:
                for sub_item in os.listdir(item_path):
                    shutil.move(os.path.join(item_path, sub_item), target_folder)
                shutil.rmtree(item_path) 
            else:
                shutil.move(item_path, target_folder)

        shutil.rmtree(extract_path)

ham_zip_1 = os.path.join(output_folder, "HAM10000_images_part_1.zip")
ham_zip_2 = os.path.join(output_folder, "HAM10000_images_part_2.zip")

print("Extracting HAM10000 images...")
extract_zip(ham_zip_1, images_folder)
extract_zip(ham_zip_2, images_folder)

segmentation_zip = os.path.join(output_folder, "HAM10000_segmentations_lesion_tschandl.zip")
if os.path.exists(segmentation_zip):
    extract_zip(segmentation_zip, segmentations_folder, remove_subfolder=True)

nested_folder = os.path.join(segmentations_folder, "HAM10000_segmentations_lesion_tschandl")
if os.path.exists(nested_folder):
    for file in os.listdir(nested_folder):
        shutil.move(os.path.join(nested_folder, file), segmentations_folder)
    shutil.rmtree(nested_folder)

metadata_file = os.path.join(output_folder, "HAM10000_metadata")
if os.path.exists(metadata_file):
    shutil.move(metadata_file, os.path.join(ham_folder, "HAM10000_metadata"))

print("Removing unnecessary files and folders...")
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

if os.path.exists(zip_file):
    os.remove(zip_file)

print("Merge complete!")
