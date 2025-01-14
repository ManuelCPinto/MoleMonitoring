import os
import pandas as pd
import matplotlib.pyplot as plt

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
plots_folder = os.path.join(root_folder, "plots")

os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv(metadata_file)

# Plot 1: Class Distribution (Ordered by Count)
class_counts = metadata["dx"].value_counts().sort_values(ascending=False)
x_labels = [f"{cls} ({metadata.loc[metadata['dx'] == cls, 'benign_malignant'].iloc[0][0]})" for cls in class_counts.index]

plt.figure(figsize=(10, 6))
plt.bar(x_labels, class_counts.values, color="skyblue")
plt.title("Class Distribution", fontsize=16)
plt.xlabel("Class", fontsize=14)
plt.ylabel("Number of Images", fontsize=14)
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
class_distribution_file = os.path.join(plots_folder, "class_distribution_histogram_ordered.png")
plt.savefig(class_distribution_file)
print(f"Class distribution plot saved to: {class_distribution_file}")
plt.show()

# Plot 2: Benign vs Malignant Comparison
benign_malignant_counts = metadata["benign_malignant"].value_counts()

plt.figure(figsize=(6, 6))
benign_malignant_counts.plot(kind="bar", color=["green", "red"])
plt.title("Benign vs Malignant Cases", fontsize=16)
plt.xlabel("Category", fontsize=14)
plt.ylabel("Number of Images", fontsize=14)
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
benign_malignant_file = os.path.join(plots_folder, "benign_vs_malignant.png")
plt.savefig(benign_malignant_file)
print(f"Benign vs malignant plot saved to: {benign_malignant_file}")
plt.show()
