import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root regardless of where script is run from
root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root / ".env", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(f"GROQ_API_KEY not found. Add it to .env file in project root.")

# Paths
CHROMA_PATH = str(root / "data" / "chroma_db")

# Initialize models and clients
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("procedures")
groq_client = Groq(api_key=GROQ_API_KEY)

def retrieve(query, n_results=5):
    embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "url": results["metadatas"][0][i]["url"],
            "score": results["distances"][0][i]
        })
    return chunks

def answer(query):
    # Error condition 1: empty query
    if not query or not query.strip():
        return "Please enter a valid question."

    chunks = retrieve(query)

    # Error condition 2: no relevant content found
    if not chunks or chunks[0]["score"] > 0.8:
        return "I could not find relevant information about that in the I-MED procedure database. Please try rephrasing your question or ask about a specific procedure like MRI, CT scan, or Ultrasound."

    # Build context
    context = ""
    sources = []
    for chunk in chunks[:3]:
        context += f"\n---\nSource: {chunk['source']} ({chunk['url']})\n{chunk['text']}\n"
        if chunk["url"] not in sources:
            sources.append(chunk["url"])

    prompt = f"""You are a helpful assistant for I-MED Radiology. Answer the patient's question using ONLY the context provided below. Do not use any outside knowledge. If the answer is not in the context, say so clearly.

Context:
{context}

Patient question: {query}

Answer (cite the source procedure name in your response):"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        answer_text = response.choices[0].message.content
        
        source_list = "\n".join([f"- {url}" for url in sources])
        return f"{answer_text}\n\n**Sources:**\n{source_list}"

    except Exception as e:
        # Error condition 3: API failure
        return f"I'm sorry, I was unable to get a response at this time. Please try again. (Error: {str(e)})"

def main():
    print("I-MED Radiology Chatbot")
    print("Ask questions about radiology procedures. Type 'quit' to exit.\n")
    
    while True:
        query = input("Your question: ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        print("\nSearching...\n")
        response = answer(query)
        print(f"Answer: {response}\n")
        print("-" * 60 + "\n")

if __name__ == "__main__":
    main()