import os
import pandas as pd

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")

test_metadata_file =  os.path.join(root_folder, "HAM10000", "ISIC2018_TestSet", "ISIC2018_Task3_Test_GroundTruth.csv")

benign_classes = ["bkl", "df", "nv", "vasc"] 
malignant_classes = ["akiec", "bcc", "mel"]  

metadata = pd.read_csv(metadata_file)
terst_metadata = pd.read_csv(test_metadata_file)

metadata["benign_malignant"] = metadata["dx"].apply(
    lambda x: "Benign" if x in benign_classes else "Malignant"
)
terst_metadata["benign_malignant"] = terst_metadata["dx"].apply(
    lambda x: "Benign" if x in benign_classes else "Malignant"
)

metadata = metadata.drop(["dataset"], axis=1)
terst_metadata = terst_metadata.drop(["dataset"], axis=1)

metadata.to_csv(metadata_file, index=False)
print(f"Metadata updated and saved to: {metadata_file}")
terst_metadata.to_csv(test_metadata_file, index=False)
print(f"Metadata updated and saved to: {test_metadata_file}")
