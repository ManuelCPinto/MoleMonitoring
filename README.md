# MoleMonitoring: Skin Mole Classification

**MoleMonitoring** is a group project developed as part of the **Samsung Innovation Campus**.  
This machine learning project focuses on multi-class classification of skin moles using dermoscopic images.

The HAM10000 dataset includes the following seven classes of skin lesions, categorized into **Benign** and **Malignant**:
### **Malignant Lesions**
- **Actinic Keratoses (`akiec`)**  
  Precancerous skin lesions that may develop into squamous cell carcinoma.

- **Basal Cell Carcinoma (`bcc`)**  
  A common and slow-growing type of skin cancer that rarely spreads.

- **Melanoma (`mel`)**  
  An aggressive and potentially fatal form of skin cancer that develops in melanocytes.
  
### **Benign Lesions**
- **Benign Keratosis-like Lesions (`bkl`)**  
  Non-cancerous growths, including seborrheic keratoses and solar lentigines.

- **Dermatofibroma (`df`)**  
  Small, firm nodules that are benign skin tumors.

- **Melanocytic Nevi (`nv`)**  
  Commonly known as moles or beauty marks, these are benign accumulations of melanocytes.

- **Vascular Lesions (`vasc`)**  
  Benign abnormalities of blood vessels, such as hemangiomas or angiomas.
  
## Team Members:

- **Manuel Pinto** - [GitHub: ManuelCPinto](https://github.com/ManuelCPinto)  
- **André Branco** - [GitHub: Aser28860d](https://github.com/Aser28860d)  
- **Francisco Silva** - [GitHub: fpgsilva](https://github.com/fpgsilva)  
- **João Pedro Silveira** - [GitHub: Joao-Pedro-Silveira](https://github.com/Joao-Pedro-Silveira)  

---
## Libraries

This project uses **TensorFlow** for image processing and model training. Ensure you have TensorFlow installed in your environment before running the project. You can install TensorFlow using pip:

```bash
pip install tensorflow
```

## Dataset Preparation

Follow these steps to download and prepare the HAM10000 dataset for this project:

### 1. Download the Dataset
1. Visit the [HAM10000 dataset page](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T).
2. Download the file named **`dataverse_files.zip`**.
3. Place the downloaded file in the root directory of the project.

### 2. Run the Preprocessing Scripts
1. Run the following commands on the project directory:
   ```bash
   python zipMerge.py
   python resizeImages.py

### 3. Output Structure
   ```bash
    MoleMonitoring/
    ├── HAM10000/
    │   ├── HAM10000_images/            # Original images from the dataset
    │   ├── HAM10000_images_processed/  # Resized images (256x256) created by `resizeImages.py`
    │   ├── HAM10000_metadata           # Updated metadata file with the `benign_malignant` column
    ├── plots/                          # Folder to store generated plots
    │   ├── class_distribution.png
    │   ├── benign_vs_malignant.png
    ├── preprocessing/                 
    │   ├── resize_images.py            # Script to resize images and store them in `HAM10000_images_processed`
    │   ├── zip_merge.py                # Script to merge and organize dataset files
    │   ├── update_metadata.py          # Script to update metadata with benign/malignant class
    │   ├── generate_plots.py           # Script to create and save plots
    ├── .gitignore                      
    ├── README.md                      

