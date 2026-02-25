import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(image_file):
    image = Image.open(image_file).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        image_features = model.get_image_features(
            pixel_values=inputs["pixel_values"]
        )

    # Direct numpy conversion (no norm for now)
    embedding = image_features[0].detach().cpu().numpy()

    return embedding