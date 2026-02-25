# recognition_utils.py
import numpy as np
import pandas as pd
from embedding_utils import get_embedding

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class InstrumentRecognizer:
    def __init__(self, embeddings_file="instrument_embeddings.csv"):
        self.df = pd.read_csv(embeddings_file)
        # Convert embedding string back to numpy array
        self.df["embedding"] = self.df["embedding"].apply(lambda x: np.array(eval(x)))

    def recognize(self, uploaded_file, top_k=1):
        query_emb = get_embedding(uploaded_file)
        sims = self.df["embedding"].apply(lambda emb: cosine_similarity(query_emb, emb))
        top_matches = sims.nlargest(top_k)
        results = self.df.loc[top_matches.index, ["file"]].copy()
        results["similarity"] = top_matches.values
        return results