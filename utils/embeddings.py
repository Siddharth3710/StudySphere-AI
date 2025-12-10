import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import streamlit as st
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
INDEX_PATH = DATA_DIR / "index.faiss"
CHUNKS_PATH = DATA_DIR / "chunks.json"


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks, model):
    vectors = model.encode(chunks)
    return np.array(vectors).astype("float32")


def create_faiss(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def save_index(index, chunks):
    """Persist FAISS index & chunks so we don't need to recompute every run."""
    faiss.write_index(index, str(INDEX_PATH))
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_persisted_index():
    """Load FAISS + chunks if they exist, else (None, None)."""
    if INDEX_PATH.exists() and CHUNKS_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        return index, chunks
    return None, None
