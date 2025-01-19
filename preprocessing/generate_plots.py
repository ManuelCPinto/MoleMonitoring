import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
plots_folder = os.path.join(root_folder, "plots")

os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv(metadata_file)

# Plot 1: Class Distribution (Ordered by Count)
class_counts = metadata["dx"].value_counts().sort_values(ascending=False)
x_labels = [f"{cls} ({metadata.loc[metadata['dx'] == cls, 'benign_malignant'].iloc[0][0]})" for cls in class_counts.index]

plt.figure(figsize=(10, 6))
bars = plt.bar(x_labels, class_counts.values, color="skyblue")
plt.title("Class Distribution", fontsize=16)
plt.xlabel("Class", fontsize=14)
plt.ylabel("Number of Images", fontsize=14)
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Add labels using bar_label
ax = plt.gca()  # Get the current Axes
ax.bar_label(bars, fmt='%d', padding=3)

plt.tight_layout()
class_distribution_file = os.path.join(plots_folder, "class_distribution_histogram_ordered.png")
plt.savefig(class_distribution_file)
print(f"Class distribution plot saved to: {class_distribution_file}")
plt.show()

# Plot 2: Benign vs Malignant Comparison
benign_malignant_counts = metadata["benign_malignant"].value_counts()

plt.figure(figsize=(6, 6))
benign_malignant_counts.plot(kind="bar", color="skyblue")
plt.title("Benign vs Malignant Cases", fontsize=16)
plt.xlabel("Category", fontsize=14)
plt.ylabel("Number of Images", fontsize=14)
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.7)

#add values to bars
ax = plt.gca()  # Get the current Axes
ax.bar_label(ax.containers[0], fmt='%d', padding=3)

plt.tight_layout()
benign_malignant_file = os.path.join(plots_folder, "benign_vs_malignant.png")
plt.savefig(benign_malignant_file)
print(f"Benign vs malignant plot saved to: {benign_malignant_file}")
plt.show()

# Plot 3: Age Distribution for Each Lesion Type
plt.figure(figsize=(12, 6))
sns.boxplot(x='dx', y='age', data=metadata, palette='muted', order=metadata['dx'].value_counts().index)
plt.title('Age Distribution by Lesion Type')
plt.xlabel('Lesion Type')
plt.ylabel('Age')
plt.xticks(rotation=45)
age_distribution_by_type_file = os.path.join(plots_folder, "age_distribution_by_type.png")
plt.savefig(age_distribution_by_type_file)
print(f"Class distribution plot saved to: {age_distribution_by_type_file}")
plt.show()

#Plot 4: Proportion of Malignant Cases by Age

age_malignancy = metadata.groupby('age')['benign_malignant'].apply(lambda x: (x == 'Malignant').mean()).reset_index()
age_malignancy.rename(columns={'benign_malignant': 'Malignant Proportion'}, inplace=True)

plt.figure(figsize=(10, 6))
plt.plot(age_malignancy['age'], age_malignancy['Malignant Proportion'], marker='o', linestyle='-', color='red')
plt.title('Proportion of Malignant Cases by Age')
plt.xlabel('Age')
plt.ylabel('Proportion of Malignant Cases')
plt.grid(alpha=0.5)
proportion_of_malignant_by_age_file = os.path.join(plots_folder, "proportion_of_malignant_by_age.png")
plt.savefig(proportion_of_malignant_by_age_file)
print(f"Class distribution plot saved to: {proportion_of_malignant_by_age_file}")
plt.show()