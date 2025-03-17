import os
import pandas as pd

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
test_metadata_file =  os.path.join(root_folder, "ISIC2018", "ISIC2018_metadata")

benign_classes = ["bkl", "df", "nv", "vasc"] 
malignant_classes = ["akiec", "bcc", "mel"]  

metadata = pd.read_csv(metadata_file)
test_metadata = pd.read_csv(test_metadata_file)

metadata["benign_malignant"] = metadata["dx"].apply(
    lambda x: "Benign" if x in benign_classes else "Malignant"
)
test_metadata["benign_malignant"] = test_metadata["dx"].apply(
    lambda x: "Benign" if x in benign_classes else "Malignant"
)

metadata = metadata.drop(["dataset"], axis=1)
test_metadata = test_metadata.drop(["dataset"], axis=1)

metadata.to_csv(metadata_file, index=False)
print(f"Metadata updated and saved to: {metadata_file}")
test_metadata.to_csv(test_metadata_file, index=False)
print(f"Metadata updated and saved to: {test_metadata_file}")