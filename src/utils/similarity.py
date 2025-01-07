import numpy as np
from typing import List

def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    except Exception as e:
        return 0.0

def calculate_histogram_similarity(hist1: List[float], hist2: List[float]) -> float:
    """Calculate similarity between two color histograms using Chi-Square distance"""
    try:
        hist1 = np.array(hist1)
        hist2 = np.array(hist2)
        
        # Chi-Square distance
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))
        
        # Convert to similarity score (0 to 1)
        similarity = np.exp(-chi_square / 2)  # Using Gaussian kernel
        
        return float(similarity)
    except Exception as e:
        return 0.0 