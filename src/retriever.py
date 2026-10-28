import json
import os
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = "data/processed_chunks/chunks.json"
CHROMA_PATH = "data/chromadb_store"

class HybridRetriever:
    def __init__(self):
        print("Loading legal chunks...")
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
            
        # 1. Lexical (BM25) Index
        self.corpus = [c["text"] for c in self.chunks]
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # 2. Dense Semantic Index (ChromaDB)
        print("Loading Sentence Transformer (all-MiniLM-L6-v2)...")
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection("legal_chunks")
        
        if self.collection.count() == 0:
            print("Embedding chunks into ChromaDB...")
            embeddings = self.embed_model.encode(self.corpus).tolist()
            ids = [c["chunk_id"] for c in self.chunks]
            metadatas = [{"case_name": c["case_name"], "p_num": c["paragraph_num"]} for c in self.chunks]
            self.collection.add(ids=ids, documents=self.corpus, embeddings=embeddings, metadatas=metadatas)
            print("Vector indexing complete.")

    def search(self, query: str, top_k: int = 3) -> list:
        # Lexical retrieval
        tokenized_q = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_q)
        top_bm25_idx = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
        
        # Dense retrieval
        q_embed = self.embed_model.encode([query]).tolist()
        dense_res = self.collection.query(query_embeddings=q_embed, n_results=top_k)
        
        results = []
        for idx in top_bm25_idx:
            chunk = self.chunks[idx]
            if chunk not in results:
                results.append(chunk)
                
        for doc_id in dense_res["ids"][0]:
            matched = next((c for c in self.chunks if c["chunk_id"] == doc_id), None)
            if matched and matched not in results:
                results.append(matched)
                
        return results[:top_k]

if __name__ == "__main__":
    retriever = HybridRetriever()
    test_q = "Section 114 amendment power"
    hits = retriever.search(test_q, top_k=2)
    print("\n--- Test Retrieval Hits ---")
    for h in hits:
        print(f"[{h['case_name']} - Para {h['paragraph_num']}] {h['text']}")