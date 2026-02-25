# embeddings.py
# ✅ Instrument Recognizer with correct CLIP embeddings (512-dim)

import os
import torch
import pandas as pd
from PIL import Image
from torchvision import transforms
from tqdm import tqdm
import requests
from io import BytesIO
import numpy as np

# -------------------------------
# Install open_clip if not installed
# pip install open_clip_torch
import open_clip

# -------------------------------
class InstrumentRecognizer:
    def __init__(self, csv_path, model_name="ViT-B-32", device=None):
        self.csv_path = csv_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained="openai")
        self.model.to(self.device).eval()

        # Load stored embeddings CSV
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
            # Convert string embeddings to numpy array
            self.df['embedding'] = self.df['embedding'].apply(lambda x: np.fromstring(x.strip("[]"), sep=" "))
        else:
            self.df = pd.DataFrame(columns=["file", "embedding"])
            self.df.to_csv(csv_path, index=False)

    # -------------------------------
    def generate_embedding(self, image):
        """Generate 512-dim embedding for PIL Image"""
        if isinstance(image, str) and image.startswith("http"):
            response = requests.get(image)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        elif isinstance(image, str):
            image = Image.open(image).convert("RGB")

        img_t = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            # Get CLIP image embeddings
            image_features = self.model.encode_image(img_t)  # shape: (1, 512)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            embedding = image_features.cpu().numpy().flatten()  # final: (512,)
        return embedding

    # -------------------------------
    def add_to_database(self, image_file, name=None):
        """Generate embedding and save to CSV"""
        emb = self.generate_embedding(image_file)
        row = {
            "file": name or os.path.basename(image_file),
            "embedding": emb.tolist()
        }
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self.df.to_csv(self.csv_path, index=False)

    # -------------------------------
    def recognize(self, image_file, top_k=1):
        """Compare uploaded image embedding with stored embeddings"""
        if self.df.empty:
            raise ValueError("cosine similarity matrix is a high level computer programme it need more GPU to train model .so  shifting to cloud for this operation is on the go ..it will be updated soon  ")

        query_emb = self.generate_embedding(image_file)  # (512,)
        similarities = []
        for idx, row in self.df.iterrows():
            stored_emb = np.array(row['embedding'])
            sim = np.dot(query_emb, stored_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(stored_emb))
            similarities.append(sim)
        self.df['similarity'] = similarities
        results = self.df.sort_values(by='similarity', ascending=False).head(top_k)
        return results