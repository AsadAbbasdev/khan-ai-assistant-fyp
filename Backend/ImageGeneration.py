import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os 
from time import sleep

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

def open_images(prompt):
    folder_path = os.path.join(PROJECT_DIR, "Data")
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)
            except Exception as e:
                print(f"Unable to open {image_path}: {e}")

# ========== ROUTER API (WORKING) ==========
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
# Alternative models:
# API_URL = "https://router.huggingface.co/hf-inference/models/ByteDance/Lite-Diffusion"
# API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-2-1"

api_key = get_key(os.path.join(PROJECT_DIR, '.env'), 'HuggingFaceAPIKey')
headers = {"Authorization": f"Bearer {api_key}"}

async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload, timeout=120)
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"[ERROR] API Error: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return None

async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        seed = randint(1, 1000000)
        payload = {
            "inputs": f"{prompt}, high quality, 4k, detailed",
            "parameters": {"seed": seed}
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            filename = os.path.join(PROJECT_DIR, "Data", f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"[SUCCESS] Image saved: {filename}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

if __name__ == "__main__":
    while True:
        try:
            file_path = os.path.join(PROJECT_DIR, "Frontend", "Files", "ImageGeneration.data")
            with open(file_path, "r") as f:
                Data = f.read().strip()

            if "," in Data:
                Prompt, Status = Data.split(",", 1)
                Prompt = Prompt.strip()
                Status = Status.strip()

                if Status == "True" and Prompt:
                    print(f"Generating: {Prompt}")
                    GenerateImages(Prompt)
                    with open(file_path, "w") as f:
                        f.write("False, False")
            sleep(1)
        except KeyboardInterrupt:
            break
        except:
            sleep(1)