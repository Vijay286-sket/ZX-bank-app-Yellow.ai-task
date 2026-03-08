import pandas as pd
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingest import ensure_index
from retriever import retrieve

def evaluate():
    ensure_index()
    csv_path = r"d:\yellow_ai Task\zxbank-assistant\Copy of ZX Bank Dataset - Sheet1.csv"
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    total = 0
    hits = 0
    exact_match_all = 0
    
    results = []
    
    for idx, row in df.iterrows():
        query = row['Query']
        facts_str = row['Supporting Facts']
        try:
            facts = json.loads(facts_str)
            expected_files = set(f['filename'] for f in facts)
        except Exception as e:
            # print(f"Error parsing json at row {idx}: {e}")
            expected_files = set()
            
        if not expected_files:
            continue
            
        retrieved_chunks, confidence = retrieve(query)
        retrieved_files = set(c['source'] for c in retrieved_chunks)
        
        # Check if AT LEAST ONE expected file is retrieved
        is_hit = bool(expected_files.intersection(retrieved_files))
        
        # Check if ALL expected files are retrieved
        is_exact = expected_files.issubset(retrieved_files)
        
        total += 1
        if is_hit:
            hits += 1
        if is_exact:
            exact_match_all += 1
            
        results.append({
            "query": query,
            "expected_files": list(expected_files),
            "retrieved_files": list(retrieved_files),
            "hit": is_hit,
            "exact": is_exact,
            "confidence": confidence
        })
        
    hit_rate = (hits / total) * 100 if total > 0 else 0
    exact_rate = (exact_match_all / total) * 100 if total > 0 else 0
    
    print("=== RETRIEVAL EVALUATION RESULTS ===")
    print(f"Total Evaluated Queries: {total}")
    print(f"Queries with at least 1 correct retrieved file: {hits} ({hit_rate:.2f}%)")
    print(f"Queries where ALL expected files were retrieved: {exact_match_all} ({exact_rate:.2f}%)")
    
    # Write detailed log
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    evaluate()
