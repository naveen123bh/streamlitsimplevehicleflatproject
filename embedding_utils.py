import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# Model load (first time thoda time lagega)
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(image_file):
    image = Image.open(image_file).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    
    return outputs[0].numpy()