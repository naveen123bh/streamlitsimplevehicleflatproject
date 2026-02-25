import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

device = "cpu"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(image_file):
    image = Image.open(image_file).convert("RGB")

    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    # normalize (important for similarity later)
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    return image_features.squeeze().cpu().numpy()