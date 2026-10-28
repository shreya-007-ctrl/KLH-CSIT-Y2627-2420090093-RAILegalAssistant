import os
import json
import re
import pdfplumber

DATA_DIR = "data/raw_judgments"
PROCESSED_DIR = "data/processed_chunks"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    return text.strip()

def extract_sections(text: str, doc_name: str) -> list:
    chunks = []
    # Extract statutes like Section 114 or Article 21
    statutes = list(set(re.findall(r'(?:Section|Article|Order|Rule)\s+\d+[A-Za-z]?', text)))
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 60]
    
    for idx, p in enumerate(paragraphs):
        cleaned_p = clean_text(p)
        if len(cleaned_p) < 40:
            continue
            
        chunks.append({
            "chunk_id": f"{doc_name}_p{idx+1}",
            "case_name": doc_name.replace(".pdf", "").replace(".txt", ""),
            "paragraph_num": idx + 1,
            "statutes_cited": statutes,
            "text": cleaned_p
        })
    return chunks

def process_all_judgments():
    os.makedirs(DATA_DIR, exist_ok=True)
    files = [f for f in os.listdir(DATA_DIR) if f.endswith((".pdf", ".txt"))]
    
    if not files:
        print(f"[!] No documents found in '{DATA_DIR}'.")
        print("[!] Generating a sample judgment file to test your pipeline...")
        sample_file = os.path.join(DATA_DIR, "sample_judgment.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("""APPELLANT: Usha Bharti
RESPONDENT: State Of U.P. & Ors
DATE OF JUDGMENT: 28/03/2014

CASE TEXT:
The earlier judgment of the High Court in the writ petition clearly merged with the judgment of the High Court dismissing the review petition.

These Rules can be amended by the High Court or the Supreme Court but Section 114 can only be amended by the Parliament. He points out that Section 121 and Section 122 permit the High Court to make its own rules on procedure.

We are unable to accept the submission that the provisions contained in Section 28 of the Act cannot be sustained in the eyes of law as it fails the test of reasonable classification under Article 14 of the Constitution.

JUDGMENT:
In view of the above observations and statutory provisions, the appeal is accordingly dismissed.""")
        files = ["sample_judgment.txt"]

    all_chunks = []
    for fname in files:
        fpath = os.path.join(DATA_DIR, fname)
        full_text = ""
        if fname.endswith(".pdf"):
            with pdfplumber.open(fpath) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        full_text += txt + "\n\n"
        else:
            with open(fpath, "r", encoding="utf-8") as f:
                full_text = f.read()
                
        chunks = extract_sections(full_text, fname)
        all_chunks.extend(chunks)
        print(f"Processed '{fname}': {len(chunks)} chunks created.")
        
    out_path = os.path.join(PROCESSED_DIR, "chunks.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"[✓] Saved {len(all_chunks)} total chunks to '{out_path}'.")

if __name__ == "__main__":
    process_all_judgments()