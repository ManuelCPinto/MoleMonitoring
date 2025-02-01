import os
import pandas as pd
import matplotlib.pyplot as plt
import stone

BASE_FOLDER = "../HAM10000"
IMAGES_FOLDER = os.path.join(BASE_FOLDER, "HAM10000_images_processed", "rgb")
METADATA_FILE = os.path.join(BASE_FOLDER, "HAM10000_metadata")
DEBUG_FOLDER = os.path.join(BASE_FOLDER, "debug_fitzpatrick")

os.makedirs(DEBUG_FOLDER, exist_ok=True)

metadata = pd.read_csv(METADATA_FILE)

FITZPATRICK_MAP = {
    "I": "I (Very Fair)",
    "II": "II (Fair)",
    "III": "III (Medium)",
    "IV": "IV (Olive)",
    "V": "V (Brown)",
    "VI": "VI (Dark Brown/Black)"
}

debug_log_path = os.path.join(DEBUG_FOLDER, "fitzpatrick_debug_log.txt")
misclassified_csv = os.path.join(DEBUG_FOLDER, "misclassified_images.csv")

with open(debug_log_path, "w") as log_file:
    log_file.write("Fitzpatrick Debug Log\n========================\n")

misclassified_images = []

def classify_fitzpatrick(hex_color):
    """ Convert hex skin tone to Fitzpatrick scale based on RGB intensity. """
    if not hex_color:
        return "Unknown"

    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    intensity = (r + g + b) / 3

    if intensity > 240:
        return "I (Very Fair)"
    elif intensity > 210:
        return "II (Fair)"
    elif intensity > 190:
        return "III (Medium)"
    elif intensity > 170:
        return "IV (Olive)"
    elif intensity > 140:
        return "V (Brown)"
    else:
        return "VI (Dark Brown/Black)"

def analyze_skin_tone(image_path, image_id):
    try:
        result = stone.process(image_path, image_type="color", return_report_image=True)

        if "faces" not in result or not result["faces"]:
            return None, None, None

        tone_label = result["faces"][0].get("tone_label", "Unknown")
        skin_hex = result["faces"][0].get("skin_tone", None)

        fitzpatrick_type = classify_fitzpatrick(skin_hex)

        with open(debug_log_path, "a") as log_file:
            log_file.write(f"{image_id}: Hex={skin_hex}, Intensity={fitzpatrick_type}, Stone_Label={tone_label}\n")

        report_images = result.get("report_images", None)
        if report_images:
            first_image = list(report_images.values())[0] 
            plt.imsave(os.path.join(DEBUG_FOLDER, f"{image_id}_report.png"), first_image)

        return fitzpatrick_type, skin_hex, tone_label

    except Exception as e:
        with open(debug_log_path, "a") as log_file:
            log_file.write(f"{image_id}: ERROR - {e}\n")
        return None, None, None

fitzpatrick_column, skin_color_column, stone_labels = [], [], []
print("🔄 Processing images... This may take a while.")

for idx, row in metadata.iterrows():
    image_id = row["image_id"]
    img_file = os.path.join(IMAGES_FOLDER, image_id + ".jpg")

    if os.path.exists(img_file):
        fitzpatrick_type, skin_hex, stone_label = analyze_skin_tone(img_file, image_id)

        if fitzpatrick_type in ["VI (Dark Brown/Black)"] and skin_hex:
            misclassified_images.append({"image_id": image_id, "hex": skin_hex, "fitzpatrick": fitzpatrick_type, "stone_label": stone_label})

        fitzpatrick_column.append(fitzpatrick_type)
        skin_color_column.append(skin_hex)
        stone_labels.append(stone_label)
    else:
        fitzpatrick_column.append("Missing Image")
        skin_color_column.append(None)
        stone_labels.append(None)

metadata["fitzpatrick_scale"] = fitzpatrick_column
metadata["skin_tone_hex"] = skin_color_column
metadata["stone_label"] = stone_labels
metadata.to_csv(METADATA_FILE, index=False)

if misclassified_images:
    pd.DataFrame(misclassified_images).to_csv(misclassified_csv, index=False)

print("\n✅ Processing Complete!")
print(f"🔹 Updated metadata saved: {METADATA_FILE}")
print(f"🔹 Debug log saved: {debug_log_path}")
if misclassified_images:
    print(f"🔹 Misclassified images log: {misclassified_csv}")
