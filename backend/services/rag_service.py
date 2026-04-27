import chromadb
from typing import List, Optional
from models.database import Bill
from rank_bm25 import BM25Okapi

class RAGService:
    """ChromaDB + BM25 Hybrid RAG pipeline"""
    
    COLLECTION_NAME = "bills"
    
    def __init__(self):
        from chromadb.config import Settings
        self.client = chromadb.PersistentClient(
            path="./chromadb_data",
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.get_or_create_collection()
        self.bm25_index = None
        self.bm25_corpus = []
        
    def get_or_create_collection(self):
        try:
            return self.client.get_collection(name=self.COLLECTION_NAME)
        except:
            return self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
    def seed_embeddings(self, bills: List[Bill]):
        """Embed bills and build BM25 dictionary"""
        if not bills:
            return
            
        ids = []
        documents = []
        metadatas = []
        texts_for_bm25 = []
        
        for bill in bills:
            text = f"Title: {bill.title}\nStatus: {bill.status}\nSummary: {bill.summary}"
            texts_for_bm25.append(text)
            
            existing = self.collection.get(ids=[bill.id])
            if existing and existing['ids'] and len(existing['ids']) > 0:
                continue

            ids.append(bill.id)
            documents.append(text)
            intro_date = bill.introduced_date.isoformat() if bill.introduced_date else ""
            metadatas.append({
                "bill_id": bill.id,
                "title": bill.title or "",
                "status": bill.status or "",
                "introduced_date": intro_date
            })
            
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
        # Build BM25
        tokenized = [t.lower().split() for t in texts_for_bm25]
        if tokenized:
            self.bm25_index = BM25Okapi(tokenized)
            self.bm25_corpus = bills
            
    def retrieve_relevant_bills(self, query: str, top_k: int = 5) -> List[dict]:
        """Hybrid Search (Chroma + BM25) with optional LLM reranking"""
        # Initial retrieval from ChromaDB
        retrieved = []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            if results and results.get("metadatas") and len(results["metadatas"]) > 0:
                for meta in results["metadatas"][0]:
                    retrieved.append(meta)
        except Exception as e:
            print(f"RAG retrieval error: {e}")

        # BM25 fallback
        if self.bm25_index:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25_index.get_scores(tokenized_query)
            top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
            for idx in top_indices:
                b = self.bm25_corpus[idx]
                if not any(r.get("bill_id") == b.id for r in retrieved):
                    retrieved.append({"bill_id": b.id, "title": b.title})

        # Optional LLM reranking if we have more candidates than needed
        if len(retrieved) > top_k:
            try:
                from langchain_openai import ChatOpenAI
                from langchain.schema import HumanMessage, SystemMessage
                docs_list = "\n".join([f"{i+1}. {doc.get('title','')} (ID: {doc.get('bill_id','')})" for i, doc in enumerate(retrieved)])
                prompt = f"Given the user query: '{query}', rank the following bills in order of relevance. Return a JSON array of bill IDs in the correct order.\n{docs_list}"
                llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
                response = llm.invoke([SystemMessage(content="You are a helpful assistant that ranks policy documents."), HumanMessage(content=prompt)])
                import json, re
                match = re.search(r"\[.*\]", response.content, re.DOTALL)
                if match:
                    ranked_ids = json.loads(match.group(0))
                    ranked = [next(d for d in retrieved if d.get('bill_id') == bid) for bid in ranked_ids if any(d.get('bill_id') == bid for d in retrieved)]
                    retrieved = ranked[:top_k]
            except Exception as e:
                print(f"LLM reranking failed: {e}")

        return retrieved[:top_k]
