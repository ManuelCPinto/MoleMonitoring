import os
import zipfile
import shutil

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
zip_file = os.path.join(base_path, "dataverse_files.zip")
output_folder = os.path.join(base_path, "dataverse_files")

ham_folder = os.path.join(base_path, "HAM10000")
images_folder = os.path.join(ham_folder, "HAM10000_images")
segmentations_folder = os.path.join(ham_folder, "HAM10000_segmentations")

test_folder = os.path.join(ham_folder, "ISIC2018_TestSet")
test_images_folder = os.path.join(test_folder, "ISIC2018_Images")  
isic_metadata_file = os.path.join(test_folder, "ISIC2018_metadata")

def extract_zip_flat(zip_path, target_folder):
    if not os.path.exists(zip_path):
        print(f"Zip does not exist: {zip_path}")
        return

    extract_path = os.path.join(target_folder, "temp_extraction")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    for root, dirs, files in os.walk(extract_path, topdown=False):
        if os.path.basename(root) == "_MACOSX":
            shutil.rmtree(root)
            continue

        for f in files:
            if f == ".DS_Store" or f.startswith("._"):
                file_to_remove = os.path.join(root, f)
                try:
                    os.remove(file_to_remove)
                except:
                    pass
                continue

            src = os.path.join(root, f)
            if os.path.isfile(src):
                dest = os.path.join(target_folder, f)
                if not os.path.exists(dest):
                    shutil.move(src, dest)

        if not os.listdir(root):
            os.rmdir(root)

    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

print("Extracting dataverse_files.zip...")
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(output_folder)

os.makedirs(images_folder, exist_ok=True)
os.makedirs(segmentations_folder, exist_ok=True)
os.makedirs(test_folder, exist_ok=True)
os.makedirs(test_images_folder, exist_ok=True)

ham_zip_1 = os.path.join(output_folder, "HAM10000_images_part_1.zip")
ham_zip_2 = os.path.join(output_folder, "HAM10000_images_part_2.zip")

print("Extracting HAM10000 images...")
extract_zip_flat(ham_zip_1, images_folder)
extract_zip_flat(ham_zip_2, images_folder)

segmentation_zip = os.path.join(output_folder, "HAM10000_segmentations_lesion_tschandl.zip")
if os.path.exists(segmentation_zip):
    extract_zip_flat(segmentation_zip, segmentations_folder)

nested_folder = os.path.join(segmentations_folder, "HAM10000_segmentations_lesion_tschandl")
if os.path.isdir(nested_folder):
    for file in os.listdir(nested_folder):
        src_path = os.path.join(nested_folder, file)
        dst_path = os.path.join(segmentations_folder, file)
        if not os.path.exists(dst_path):
            shutil.move(src_path, dst_path)
    shutil.rmtree(nested_folder)

ham_metadata_source = os.path.join(output_folder, "HAM10000_metadata")
ham_metadata_target = os.path.join(ham_folder, "HAM10000_metadata")
if os.path.exists(ham_metadata_source):
    shutil.move(ham_metadata_source, ham_metadata_target)

test_images_zip = os.path.join(output_folder, "ISIC2018_Task3_Test_Images.zip")
if os.path.exists(test_images_zip):
    extract_zip_flat(test_images_zip, test_images_folder)

groundtruth_csv = os.path.join(output_folder, "ISIC2018_Task3_Test_GroundTruth.csv")
if os.path.exists(groundtruth_csv):
    shutil.move(groundtruth_csv, isic_metadata_file)

unwanted_csv = os.path.join(output_folder, "ISIC2018_Task3_NatureMedicine_AI_Images.csv")
if os.path.exists(unwanted_csv):
    os.remove(unwanted_csv)

print("Removing unnecessary files and folders...")
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
if os.path.exists(zip_file):
    os.remove(zip_file)