import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
plots_folder = os.path.join(root_folder, "plots")

os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv(metadata_file)

bar_color="#87CEEB"

# Plot 1: Class Distribution (Ordered by Count)
class_counts = metadata["dx"].value_counts().sort_values(ascending=False)
x_labels = [f"{cls} ({metadata.loc[metadata['dx'] == cls, 'benign_malignant'].iloc[0][0]})" for cls in class_counts.index]

plt.figure(figsize=(10, 6))
bars = plt.bar(x_labels, class_counts.values, color=bar_color)
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
benign_malignant_counts.plot(kind="bar", color=bar_color)
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



# Plot 4: Proportion of Malignant Cases by Age

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



# Plot 5: Distribution plot for 'age' (numerical column)
plt.figure(figsize=(8, 6))
sns.histplot(metadata['age'], kde=True, bins=30, color=bar_color, alpha=0.7)
plt.title("Distribution of Age")
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.savefig(os.path.join(plots_folder, "distribution_age.png"))
plt.show()
plt.close()



# Plot 6: Order categories by count for 'sex'
sex_order = metadata['sex'].value_counts().index

plt.figure(figsize=(8, 6))
sns.countplot(data=metadata, x='sex', order=sex_order, color=bar_color, alpha=0.7)
plt.title("Count Plot of Gender")
plt.xlabel("Gender")
plt.ylabel("Count")

ax = plt.gca()  # Get the current Axes
ax.bar_label(ax.containers[0], fmt='%d', padding=3)

plt.show()
plt.close()



# Plot 7: Order categories by count for 'localization'
localization_order = metadata['localization'].value_counts().index

plt.figure(figsize=(10, 6))
sns.countplot(data=metadata, x='localization', order=localization_order, color=bar_color, alpha=0.7)
plt.title("Count Plot of Localization")
plt.xlabel("Localization")
plt.ylabel("Count")

ax = plt.gca()  # Get the current Axes
ax.bar_label(ax.containers[0], fmt='%d', padding=3)

plt.xticks(rotation=45)
plt.show()
plt.close()



# Plot 8: Aggregate counts and sort by 'sex' and 'dx'
aggregated_data = (
    metadata.groupby(['sex', 'dx']).size().reset_index(name='count')
)
aggregated_data = aggregated_data.sort_values(['sex', 'count'], ascending=[True, False])

# Reorder hue categories (dx) based on the total count across all 'sex'
dx_order = metadata['dx'].value_counts().index

# Reorder x categories (sex) based on aggregated counts
sex_order = aggregated_data['sex'].unique()

plt.figure(figsize=(8, 6))
sns.countplot(
    data=metadata,
    x='sex',
    hue='dx',
    order=sex_order,
    hue_order=dx_order,
    palette='Spectral'
)
plt.title("Distribution of Gender by dx (Ordered)")
plt.xlabel("Gender")
plt.ylabel("Count")
plt.show()
plt.close()



# Plot 9: Aggregate counts and sort for 'localization' by 'dx'
aggregated_localization = (
    metadata.groupby(['localization', 'dx']).size().reset_index(name='count')
)
aggregated_localization = aggregated_localization.sort_values(['localization', 'count'], ascending=[True, False])

# Reorder hue categories (dx) based on total count across all 'localization'
dx_order_localization = metadata['dx'].value_counts().index

# Reorder x categories (localization) based on aggregated counts
localization_order = aggregated_localization['localization'].unique()

plt.figure(figsize=(10, 6))
sns.countplot(
    data=metadata,
    x='localization',
    hue='dx',
    order=localization_order,
    hue_order=dx_order_localization,
    palette='Spectral'
)
plt.title("Distribution of Localization by dx (Ordered)")
plt.xlabel("Localization")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.show()
plt.close()



# Plot 10: Aggregate counts and sort for 'benign_malignant' by 'dx'
aggregated_benign_malignant = (
    metadata.groupby(['benign_malignant', 'dx']).size().reset_index(name='count')
)
aggregated_benign_malignant = aggregated_benign_malignant.sort_values(['benign_malignant', 'count'], ascending=[True, False])

# Reorder hue categories (dx) based on total count across all 'benign_malignant'
dx_order_benign_malignant = metadata['dx'].value_counts().index

# Reorder x categories (benign_malignant) based on aggregated counts
benign_malignant_order = aggregated_benign_malignant['benign_malignant'].unique()

plt.figure(figsize=(8, 6))
sns.countplot(
    data=metadata,
    x='benign_malignant',
    hue='dx',
    order=benign_malignant_order,
    hue_order=dx_order_benign_malignant,
    palette='Spectral'
)
plt.title("Distribution of Benign/Malignant by dx (Ordered)")
plt.xlabel("Benign or Malignant")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.show()
plt.close()