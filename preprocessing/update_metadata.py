import os
import pandas as pd

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")

benign_classes = ["bkl", "df", "nv", "vasc"] 
malignant_classes = ["akiec", "bcc", "mel"]  

metadata = pd.read_csv(metadata_file)

metadata["benign_malignant"] = metadata["dx"].apply(
    lambda x: "Benign" if x in benign_classes else "Malignant"
)

# Removed unecessary colums
metadata = metadata.drop(["image_id", "dataset"], axis=1)

metadata.to_csv(metadata_file, index=False)
print(f"Metadata updated and saved to: {metadata_file}")
