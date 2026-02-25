# embeddings.py
# This handles Google Drive image URLs and instrument recognition
import pandas as pd
import torch
from PIL import Image
import requests
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel
import numpy as np

class InstrumentRecognizer:
    def __init__(self, csv_path):
        """
        csv_path: path to CSV file containing 'item_name' and 'image_url' columns
        """
        self.df = pd.read_csv(csv_path)
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Precompute embeddings for all items in CSV
        self.df["embedding"] = self.df["image_url"].apply(self._get_image_embedding)

    def _get_image_embedding(self, url):
        try:
            # Convert Google Drive URL to direct download link if needed
            if "/d/" in url:
                file_id = url.split("/d/")[1].split("/")[0]
                url = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            inputs = self.processor(images=img, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.get_image_features(**inputs)
            embedding = outputs[0].cpu().numpy()
            # Normalize
            embedding /= np.linalg.norm(embedding)
            return embedding
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def recognize(self, uploaded_file, top_k=3):
        """
        uploaded_file: Streamlit uploaded file
        top_k: number of top matches to return
        """
        img = Image.open(uploaded_file).convert("RGB")
        inputs = self.processor(images=img, return_tensors="pt").to(self.device)
        with torch.no_grad():
            uploaded_embedding = self.model.get_image_features(**inputs)[0].cpu().numpy()
        uploaded_embedding /= np.linalg.norm(uploaded_embedding)

        # Calculate cosine similarity
        sims = []
        for idx, row in self.df.iterrows():
            if row["embedding"] is None:
                sims.append(-1)
                continue
            sim = np.dot(uploaded_embedding, row["embedding"])
            sims.append(sim)

        self.df["similarity"] = sims
        top_matches = self.df.sort_values("similarity", ascending=False).head(top_k)
        return top_matches[["item_name", "image_url", "similarity"]].reset_index(drop=True)