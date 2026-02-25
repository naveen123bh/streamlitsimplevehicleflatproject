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
        outputs = model(**inputs)
        image_features = outputs.image_embeds   # 👈 सही feature यहीं है

    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    return image_features[0].numpy()