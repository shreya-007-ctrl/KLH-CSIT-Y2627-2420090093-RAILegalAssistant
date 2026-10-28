from retriever import HybridRetriever

class LegalAssistant:
    def __init__(self):
        self.retriever = HybridRetriever()
        
    def generate_grounded_response(self, query: str) -> dict:
        retrieved_chunks = self.retriever.search(query, top_k=3)
        
        if not retrieved_chunks:
            return {
                "answer": "INSUFFICIENT EVIDENCE: The provided judgment records do not address this query.",
                "sources": [],
                "confidence": "Low"
            }
            
        sources = []
        answer = "Based on the retrieved judgments:\n\n"
        for i, chunk in enumerate(retrieved_chunks):
            tag = f"[{i+1}]"
            sources.append({
                "tag": tag,
                "case": chunk["case_name"],
                "paragraph": chunk["paragraph_num"],
                "text": chunk["text"],
                "statutes": chunk.get("statutes_cited", [])
            })
            answer += f"• In **{chunk['case_name']}** (Paragraph {chunk['paragraph_num']}) {tag}, the record states: \"{chunk['text']}\"\n\n"
            
        return {
            "answer": answer,
            "sources": sources,
            "confidence": "High" if len(sources) > 0 else "Low"
        }

if __name__ == "__main__":
    assistant = LegalAssistant()
    res = assistant.generate_grounded_response("What did the court state regarding Section 114?")
    print(res["answer"])