import hashlib
import numpy as np
from typing import List, Dict, Any, Tuple
from src.models import EMBEDDING_DIM

def generate_mock_embedding(text_content: str) -> List[float]:
    """
    Generates a deterministic, normalized 384-dimensional dense float vector 
    derived from text content (skills / job descriptions) for testing & search evaluation.
    """
    seed_bytes = hashlib.sha256(text_content.lower().encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(seed_bytes[:4], "big"))
    vec = rng.normal(loc=0.0, scale=1.0, size=EMBEDDING_DIM)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec.tolist()
    return (vec / norm).tolist()


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates cosine similarity between two 384-dimensional vectors."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def analyze_skill_gaps(candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Compares candidate skills against target job benchmark requirements to isolate 
    acquired skills, missing critical skills, and overall coverage percentage.
    """
    candidate_set = {s.strip().lower() for s in candidate_skills}
    required_set = {s.strip().lower() for s in required_skills}

    acquired = sorted(list(candidate_set.intersection(required_set)))
    missing = sorted(list(required_set.difference(candidate_set)))
    
    coverage_percentage = (len(acquired) / len(required_set) * 100.0) if required_set else 100.0

    return {
        "acquired_skills": acquired,
        "missing_skills": missing,
        "acquired_count": len(acquired),
        "missing_count": len(missing),
        "skill_coverage_pct": round(coverage_percentage, 2)
    }
