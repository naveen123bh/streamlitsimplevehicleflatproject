import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(image_file):
    image = Image.open(image_file).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        image_features = model.get_image_features(
            pixel_values=inputs["pixel_values"]
        )

    # Convert properly to numpy
    embedding = image_features.cpu().numpy()

    return embedding[0]