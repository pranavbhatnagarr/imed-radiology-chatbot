import json
import os
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

def chunk_text(text, chunk_size=400, overlap=50):
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def build_vector_store():
    # Load scraped data
    with open("data/procedures.json", "r") as f:
        procedures = json.load(f)

    # Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    # Set up ChromaDB
    client = chromadb.PersistentClient(path="data/chroma_db")
    
    # Delete existing collection if it exists
    try:
        client.delete_collection("procedures")
    except:
        pass
    
    collection = client.create_collection("procedures")

    total_chunks = 0
    for procedure in procedures:
        if procedure["status"] != "success" or not procedure["content"]:
            print(f"Skipping {procedure['name']} (no content)")
            continue

        chunks = chunk_text(procedure["content"])
        print(f"Embedding {procedure['name']}: {len(chunks)} chunks...")

        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()
            collection.add(
                ids=[f"{procedure['name']}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": procedure["name"],
                    "url": procedure["url"],
                    "chunk_index": i
                }]
            )
            total_chunks += 1

    print(f"\nDone! Stored {total_chunks} chunks in ChromaDB.")

if __name__ == "__main__":
    build_vector_store()