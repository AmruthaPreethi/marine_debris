from pathlib import Path
import shutil

SOURCE = Path(
    r"C:\Users\Amrutha\.cache\kagglehub\datasets\mawins"
    r"\side-scan-sonar-image-for-object-detection\versions\1\Combined_Dataset"
)

DEST = Path("training/Combined_Dataset_5class")

for split in ["train", "val", "test"]:
    src_images = SOURCE / split / "images"
    src_labels = SOURCE / split / "labels"

    dst_images = DEST / split / "images"
    dst_labels = DEST / split / "labels"

    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    print(f"\nPreparing {split}...")

    # Copy images
    for image in src_images.iterdir():
        if image.is_file():
            shutil.copy2(image, dst_images / image.name)

    # Copy and modify labels
    for label in src_labels.glob("*.txt"):
        new_label = dst_labels / label.name

        lines = label.read_text().splitlines()

        # Find corresponding image
        image_stem = label.stem
        is_cylinder = image_stem.startswith("Cylinder_")

        new_lines = []

        for line in lines:
            parts = line.split()

            if not parts:
                continue

            # Cylinder objects are currently ID 2.
            # Convert ONLY Cylinder-labelled files from 2 -> 4.
            if is_cylinder and parts[0] == "2":
                parts[0] = "4"

            new_lines.append(" ".join(parts))

        new_label.write_text("\n".join(new_lines))

    print(f"{split} complete.")

print("\n5-class dataset created at:")
print(DEST.resolve())