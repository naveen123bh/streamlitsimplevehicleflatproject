# build_embeddings.py
import os
import pandas as pd
from embedding_utils import get_embedding

IMAGE_FOLDER = "instrument_images"  # सब images यहीं रखो
OUTPUT_FILE = "instrument_embeddings.csv"

data = []

for fname in os.listdir(IMAGE_FOLDER):
    if fname.lower().endswith((".jpg", ".png", ".jpeg")):
        filepath = os.path.join(IMAGE_FOLDER, fname)
        try:
            emb = get_embedding(filepath)  # 512-dim
            # store as list
            data.append({
                "file": fname,
                "embedding": emb.tolist()  # CSV storeable
            })
        except Exception as e:
            print(f"Skipping {fname}: {e}")

df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved {len(df)} embeddings to {OUTPUT_FILE}")