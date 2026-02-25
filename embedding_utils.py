# embedding_utils.py
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

# 🔹 Load CLIP model and processor (vision only)
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(image_file):
    """
    Input: file-like object or path of an image
    Output: 512-dim numpy array embedding
    """
    # Open image
    image = Image.open(image_file).convert("RGB")

    # Preprocess image
    inputs = processor(images=image, return_tensors="pt")

    # Forward pass through vision encoder
    with torch.no_grad():
        # Vision model forward
        vision_outputs = model.vision_model(
            pixel_values=inputs["pixel_values"]
        )

        # pooled output → (batch_size, hidden_dim)
        pooled_output = vision_outputs.pooler_output

        # Visual projection → final 512-dim embedding
        image_features = model.visual_projection(pooled_output)

    # Convert to numpy array
    embedding = image_features.detach().numpy()[0]

    return embedding