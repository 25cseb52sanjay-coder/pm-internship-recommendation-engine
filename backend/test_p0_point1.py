import sys
import numpy as np
from app.services.recommendation import compute_semantic_similarity

def test_ai_vector_embedding_model():
    print("\n======================================================================")
    print("  AUDIT TEST: P0 POINT 1 — REAL AI/ML VECTOR EMBEDDING MODEL")
    print("======================================================================\n")

    text_candidate_ai = "B.Tech Computer Science student specializing in Machine Learning, Deep Learning, Python, PyTorch, PySpark, and Cloud Data Pipelines."
    text_internship_ai = "Looking for an AI & Data Science Intern with strong hands-on skills in Python, Neural Networks, PyTorch, and Big Data ML engineering."
    text_internship_civil = "Seeking a Civil Engineering Construction Trainee for structural building design, CAD drafting, site survey, and concrete inspection."

    # 1. Compute Semantic Vector Similarity for High Semantic Match
    score_ai_match = compute_semantic_similarity(text_candidate_ai, text_internship_ai)
    print(f"  [1] High Semantic Match Pair Score: {score_ai_match}%")
    assert score_ai_match >= 75.0, f"Expected high semantic similarity (>= 75.0%), got {score_ai_match}%"

    # 2. Compute Semantic Vector Similarity for Low Semantic Match (Civil Eng vs AI Candidate)
    score_civil_match = compute_semantic_similarity(text_candidate_ai, text_internship_civil)
    print(f"  [2] Low Semantic Match Pair Score:  {score_civil_match}%")
    assert score_civil_match < score_ai_match, f"Expected low semantic score < high match score ({score_ai_match}%), got {score_civil_match}%"

    print("\n======================================================================")
    print("  VERIFICATION RESULT: P0 POINT 1 PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_ai_vector_embedding_model()
