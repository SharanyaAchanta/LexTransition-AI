"""
Evaluation module for Hybrid Retrieval Pipeline.

This module provides:
- Precision@K
- Recall@K
- MRR (Mean Reciprocal Rank)
- Structured comparison output
"""

from typing import List, Dict

def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    Calculate Precision@K
    Precision@K = (# relevant items in top K) / K
    """
    if k == 0:
        return 0.0

    top_k = retrieved[:k]
    relevant_set = set(relevant)

    relevant_count = sum(1 for item in top_k if item in relevant_set)

    return relevant_count / k


def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    Calculate Recall@K
    Recall@K = (# relevant items in top K) / (total relevant items)
    """
    if not relevant:
        return 0.0

    top_k = retrieved[:k]
    relevant_set = set(relevant)

    relevant_count = sum(1 for item in top_k if item in relevant_set)

    return relevant_count / len(relevant_set)

def mean_reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR)
    For a single query:
    MRR = 1 / rank_of_first_relevant
    """
    relevant_set = set(relevant)

    for rank, item in enumerate(retrieved, start=1):
        if item in relevant_set:
            return 1.0 / rank

    return 0.0

def evaluate_retrieval(
    retrieved: List[str],
    relevant: List[str],
    k: int = 5
) -> Dict[str, float]:
    """
    Return structured evaluation results
    """
    return {
        "precision_at_k": precision_at_k(retrieved, relevant, k),
        "recall_at_k": recall_at_k(retrieved, relevant, k),
        "mrr": mean_reciprocal_rank(retrieved, relevant),
    }