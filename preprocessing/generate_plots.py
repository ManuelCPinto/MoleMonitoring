import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_class_distribution(metadata, plots_folder):
    class_counts = metadata["dx"].value_counts().sort_values(ascending=False)
    x_labels = [f"{cls} ({metadata.loc[metadata['dx'] == cls, 'benign_malignant'].iloc[0][0]})" for cls in class_counts.index]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(x_labels, class_counts.values, color="#87CEEB")
    plt.title("Class Distribution", fontsize=16)
    plt.xlabel("Class", fontsize=14)
    plt.ylabel("Number of Images", fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.gca().bar_label(bars, fmt='%d', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "class_distribution_histogram_ordered.png"))
    plt.show()

def plot_benign_vs_malignant(metadata, plots_folder):
    benign_malignant_counts = metadata["benign_malignant"].value_counts()
    
    plt.figure(figsize=(6, 6))
    benign_malignant_counts.plot(kind="bar", color="#87CEEB")
    plt.title("Benign vs Malignant Cases", fontsize=16)
    plt.xlabel("Category", fontsize=14)
    plt.ylabel("Number of Images", fontsize=14)
    plt.xticks(rotation=0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.gca().bar_label(plt.gca().containers[0], fmt='%d', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "benign_vs_malignant.png"))
    plt.show()

def plot_age_distribution_by_type(metadata, plots_folder):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='dx', y='age', data=metadata, palette='muted', order=metadata['dx'].value_counts().index)
    plt.title('Age Distribution by Lesion Type')
    plt.xlabel('Lesion Type')
    plt.ylabel('Age')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "age_distribution_by_type.png"))
    plt.show()

def plot_proportion_malignant_by_age(metadata, plots_folder):
    age_malignancy = metadata.groupby('age')['benign_malignant'].apply(lambda x: (x == 'Malignant').mean()).reset_index()
    age_malignancy.rename(columns={'benign_malignant': 'Malignant Proportion'}, inplace=True)

    plt.figure(figsize=(10, 6))
    plt.plot(age_malignancy['age'], age_malignancy['Malignant Proportion'], marker='o', linestyle='-', color='red')
    plt.title('Proportion of Malignant Cases by Age')
    plt.xlabel('Age')
    plt.ylabel('Proportion of Malignant Cases')
    plt.grid(alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "proportion_of_malignant_by_age.png"))
    plt.show()

def plot_age_distribution(metadata, plots_folder):
    plt.figure(figsize=(8, 6))
    sns.histplot(metadata['age'], kde=True, bins=30, color="#87CEEB", alpha=0.7)
    plt.title("Distribution of Age")
    plt.xlabel("Age")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "distribution_age.png"))
    plt.show()

def plot_gender_distribution(metadata, plots_folder):
    plt.figure(figsize=(8, 6))
    sns.countplot(data=metadata, x='sex', order=metadata['sex'].value_counts().index, color="#87CEEB", alpha=0.7)
    plt.title("Count Plot of Gender")
    plt.xlabel("Gender")
    plt.ylabel("Count")
    plt.gca().bar_label(plt.gca().containers[0], fmt='%d', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "gender_distribution.png"))
    plt.show()

def plot_localization_distribution(metadata, plots_folder):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=metadata, x='localization', order=metadata['localization'].value_counts().index, color="#87CEEB", alpha=0.7)
    plt.title("Count Plot of Localization")
    plt.xlabel("Localization")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.gca().bar_label(plt.gca().containers[0], fmt='%d', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "localization_distribution.png"))
    plt.show()

def plot_gender_by_dx(metadata, plots_folder):
    aggregated_data = metadata.groupby(['sex', 'dx']).size().reset_index(name='count')
    aggregated_data = aggregated_data.sort_values(['sex', 'count'], ascending=[True, False])

    dx_order = metadata['dx'].value_counts().index
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
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "gender_by_dx.png"))
    plt.show()

def plot_localization_by_dx(metadata, plots_folder):
    aggregated_localization = metadata.groupby(['localization', 'dx']).size().reset_index(name='count')
    aggregated_localization = aggregated_localization.sort_values(['localization', 'count'], ascending=[True, False])

    dx_order_localization = metadata['dx'].value_counts().index
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
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "localization_by_dx.png"))
    plt.show()

def plot_benign_malignant_by_dx(metadata, plots_folder):
    aggregated_benign_malignant = metadata.groupby(['benign_malignant', 'dx']).size().reset_index(name='count')
    aggregated_benign_malignant = aggregated_benign_malignant.sort_values(['benign_malignant', 'count'], ascending=[True, False])

    dx_order_benign_malignant = metadata['dx'].value_counts().index
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
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "benign_malignant_by_dx.png"))
    plt.show()

def plot_psnr_histogram(metrics, plots_folder):
    psnr_bins = [0, 29, 39, float('inf')]
    psnr_labels = ['0-29 (Bad)', '30-39 (Ok)', '40+ (Good)']
    metrics['PSNR_Category'] = pd.cut(metrics['PSNR'], bins=psnr_bins, labels=psnr_labels, right=True)

    psnr_counts = metrics['PSNR_Category'].value_counts().sort_index()

    plt.figure(figsize=(8, 6))
    sns.barplot(x=psnr_counts.index, y=psnr_counts.values, palette='Blues_d', alpha=0.8)
    plt.title("Image Count by PSNR Range", fontsize=16)
    plt.xlabel("PSNR Range", fontsize=14)
    plt.ylabel("Number of Images", fontsize=14)

    for i, value in enumerate(psnr_counts.values):
        plt.text(i, value + 1, str(value), ha='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "psnr_histogram.png"))
    plt.show()

def plot_ssim_histogram(metrics, plots_folder):
    ssim_bins = [0, 0.7, 0.9, 1.0]
    ssim_labels = ['0-0.7 (Bad)', '0.7-0.9 (Ok)', '0.9-1.0 (Good)']
    metrics['SSIM_Category'] = pd.cut(metrics['SSIM'], bins=ssim_bins, labels=ssim_labels, right=True)

    ssim_counts = metrics['SSIM_Category'].value_counts().sort_index()

    plt.figure(figsize=(8, 6))
    sns.barplot(x=ssim_counts.index, y=ssim_counts.values, palette='Greens_d', alpha=0.8)
    plt.title("Image Count by SSIM Range", fontsize=16)
    plt.xlabel("SSIM Range", fontsize=14)
    plt.ylabel("Number of Images", fontsize=14)

    for i, value in enumerate(ssim_counts.values):
        plt.text(i, value + 1, str(value), ha='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, "ssim_histogram.png"))
    plt.show()

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

plots_folder = os.path.join(root_folder, "plots")
os.makedirs(plots_folder, exist_ok=True)

metadata = pd.read_csv( os.path.join(root_folder, "HAM10000", "HAM10000_metadata"))
metrics = pd.read_csv(os.path.join(root_folder, "HAM10000", "HAM10000_images_processed", "metrics", "hair_removal_metrics.csv"))

plot_class_distribution(metadata, plots_folder)
plot_benign_vs_malignant(metadata, plots_folder)
plot_age_distribution_by_type(metadata, plots_folder)
plot_proportion_malignant_by_age(metadata, plots_folder)
plot_age_distribution(metadata, plots_folder)
plot_gender_distribution(metadata, plots_folder)
plot_localization_distribution(metadata, plots_folder)
plot_gender_by_dx(metadata, plots_folder)
plot_localization_by_dx(metadata, plots_folder)
plot_benign_malignant_by_dx(metadata, plots_folder)
plot_psnr_histogram(metrics, plots_folder)
plot_ssim_histogram(metrics, plots_folder)

