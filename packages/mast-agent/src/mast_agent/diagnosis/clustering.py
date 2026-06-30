import os
import uuid
import math
from typing import List, Dict

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

class FailureClusterer:
    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold
        self.embeddings_model = None
        
        # Try to initialize OpenAI embeddings if available
        if os.getenv("OPENAI_API_KEY"):
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embeddings_model = OpenAIEmbeddings()
            except ImportError:
                pass

    def _get_embedding(self, text: str) -> List[float]:
        if self.embeddings_model:
            return self.embeddings_model.embed_query(text)
        # Dummy embedding for fallback: a very naive character frequency vector
        # (Only useful to make the code run if no API key is provided)
        vec = [0.0] * 26
        for char in text.lower():
            if 'a' <= char <= 'z':
                vec[ord(char) - ord('a')] += 1.0
        return vec

    async def cluster_diagnoses(self, diagnoses: List[Dict]) -> List[Dict]:
        """
        Group similar root causes using embedding + cosine similarity.
        Expects a list of dicts with 'id', 'failure_mode', 'root_cause'
        """
        clusters = []
        for diag in diagnoses:
            root_cause = diag["root_cause"]
            emb = self._get_embedding(root_cause)
            
            matched = False
            for cluster in clusters:
                if cluster["failure_mode"] != diag["failure_mode"]:
                    continue # Only cluster within same failure mode
                    
                # Compare to representative
                sim = cosine_similarity(emb, cluster["_rep_embedding"])
                if sim >= self.threshold:
                    cluster["count"] += 1
                    cluster["diagnosis_ids"].append(diag["id"])
                    matched = True
                    break
            
            if not matched:
                clusters.append({
                    "id": str(uuid.uuid4()),
                    "representative_cause": root_cause,
                    "failure_mode": diag["failure_mode"],
                    "count": 1,
                    "diagnosis_ids": [diag["id"]],
                    "_rep_embedding": emb
                })
        
        # Cleanup internal keys and return sorted
        for c in clusters:
            del c["_rep_embedding"]
            
        return sorted(clusters, key=lambda x: x["count"], reverse=True)
