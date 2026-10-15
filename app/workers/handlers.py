import time
import json
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
import os

# constants
load_dotenv("./app/.env")
ROOT_DIR = Path(os.getenv("ROOT_DIR"))
ASSETS_DIR = Path(os.getenv("ASSETS_DIR"))
IMG_DIR = Path(os.getenv("IMG_DIR"))
IMG_OUTPUT_DIR = Path(os.getenv("IMG_OUTPUT_DIR"))
IMG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DESIRED_QUALITY = [2, 25, 50, 75]


# ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# IMG_DIR = ROOT_DIR / "assets" / "image"
# IMG_OUTPUT_DIR = ROOT_DIR / "assets" / "output_images"
# IMG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# task executor
def task_executor(job,payload):
    if job.type == "sleep":
        seconds = int(payload["seconds"])

        result = sleep_handler(seconds)
        job.result = result
        return result

    elif job.type == "calculation":
        first = payload["first"]
        second = payload["second"]
        operator = payload["operator"]

        result = calculation_handler(first,second,operator)
        job.result = result
        return result

    elif job.type == "image":
        image = payload["image_path"]

        result = image_handler(image)
        job.result = result
        return result

    else:
        raise TypeError("Invalid Job Type Received")

# Calculation handler
def calculation_handler(first:str,second:str,operator:str):
    if operator == "+":
        result = int(first) + int(second)
    elif operator == "-":
        result = int(first) - int(second)
    elif operator == "*":
        result = int(first) * int(second)
    elif operator == "/":
        result = int(first) / int(second)
    elif operator == "//":
        result = int(first) // int(second)
    elif operator == "**":
        result = int(first) ** int(second)
    else:
        raise ValueError(f"Unsupported Operator")

    return json.dumps({
        "result": str(result)
    })

# Sleep handler
def sleep_handler(seconds:str):
    time.sleep(seconds)

    return json.dumps({
        "result": f"Slept for {seconds}s"
    })

# image handler
def image_handler(image_path):
    result = []

    image_path = IMG_DIR / image_path
    print(image_path)
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            for quality in DESIRED_QUALITY:
                img_output = IMG_OUTPUT_DIR / f"{Path(image_path).stem}_{quality}.jpg"
                img.save(img_output, "JPEG", quality=quality, optimize=True)

                result.append({
                    "quality": quality,
                    "path": str(img_output)
                })
    except:
        raise FileNotFoundError

    return json.dumps(result)
    