from sentence_transformers import SentenceTransformer
import numpy as np
import torch

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    v = model.encode("hello")
    print(f"Shape: {v.shape}")
except Exception as e:
    print(f"Error: {e}")
