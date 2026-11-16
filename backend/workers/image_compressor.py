from PIL import Image
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
IMG_DIR = ROOT_DIR / "assets" / "image"
IMG_OUTPUT_DIR = ROOT_DIR / "assets" / "output_images"

IMG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

desired_qualities = [2, 25, 50, 75]

for image in IMG_DIR.glob("*.png"):
    with Image.open(image) as img:
        img = img.convert("RGB")

        for quality in desired_qualities:
            img_output = IMG_OUTPUT_DIR / f"{image.stem}_{quality}.jpg"
            img.save(img_output, "JPEG", quality=quality, optimize=True)