import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
metadata_file = os.path.join(root_folder, "HAM10000", "HAM10000_metadata")
plots_folder = os.path.join(root_folder, "plots")
os.makedirs(plots_folder, exist_ok=True)

# Load data
metadata = pd.read_csv(metadata_file)

# Drop potentially useless columns
metadata.drop(['lesion_id', 'image_id'], axis=1, inplace=True)

# Summary statistics and value counts
eda_summary = {}

# Individual column analysis
for col in metadata.columns:
    if metadata[col].dtype == 'object':
        eda_summary[col] = metadata[col].value_counts()
    else:
        eda_summary[col] = metadata[col].describe()

# Save summary statistics to a file
summary_file = os.path.join(plots_folder, "eda_summary.txt")
with open(summary_file, "w") as f:
    for col, stats in eda_summary.items():
        f.write(f"Column: {col}\n{stats}\n\n")

# Distribution plot for 'age' (numerical column)
plt.figure(figsize=(8, 6))
sns.histplot(metadata['age'], kde=True, bins=30, color='blue', alpha=0.7)
plt.title("Distribution of Age")
plt.xlabel("Age")
plt.ylabel("Frequency")
#plt.savefig(os.path.join(plots_folder, "distribution_age.png"))
plt.show()
plt.close()

# Count plots for categorical columns
categorical_cols = metadata.select_dtypes(include=['object']).columns
for col in categorical_cols:
    plt.figure(figsize=(8, 6))
    sns.countplot(y=col, data=metadata, order=metadata[col].value_counts().index, palette="viridis")
    plt.title(f"Count Plot of {col}")
    plt.xlabel("Count")
    plt.ylabel(col)
    #plt.savefig(os.path.join(plots_folder, f"countplot_{col}.png"))
    plt.show()
    plt.close()

# Relationships between categorical columns and 'dx'
for col in categorical_cols:
    if col != 'dx':
        plt.figure(figsize=(8, 6))
        sns.countplot(data=metadata, x=col, hue="dx", palette="Spectral")
        plt.title(f"Distribution of {col} by dx")
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        #plt.savefig(os.path.join(plots_folder, f"{col}_by_dx.png"))
        plt.show()
        plt.close()

# Box plot for age by 'dx'
plt.figure(figsize=(10, 6))
sns.boxplot(data=metadata, x="dx", y="age", palette="Set3")
plt.title("Age Distribution by dx")
plt.xlabel("dx")
plt.ylabel("Age")
plt.xticks(rotation=45)
#plt.savefig(os.path.join(plots_folder, "age_by_dx.png"))
plt.show()
plt.close()

# Correlation matrix (one-hot encode categorical variables)
encoded_metadata = pd.get_dummies(metadata, drop_first=True)
correlation_matrix = encoded_metadata.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=False, cmap="coolwarm", cbar=True)
plt.title("Correlation Matrix (One-Hot Encoded)")
#plt.savefig(os.path.join(plots_folder, "correlation_matrix_encoded.png"))
plt.show()
plt.close()

# Pairwise relationships with 'dx'
sns.pairplot(metadata, hue='dx', diag_kind='kde', palette="Set2", corner=True, vars=['age'])
#plt.savefig(os.path.join(plots_folder, "pairplot_dx.png"))
plt.show()
plt.close()

# Check missing values
missing_values = metadata.isnull().sum()
missing_file = os.path.join(plots_folder, "missing_values.txt")
with open(missing_file, "w") as f:
    f.write("Missing Values:\n")
    f.write(missing_values.to_string())

print(f"EDA complete. Plots saved in {plots_folder}")
