import cv2
import numpy as np
import requests
from io import BytesIO
from typing import List
import logging

logger = logging.getLogger(__name__)

async def get_color_histogram_embedding(img_url: str) -> List[float]:
    """Get color histogram embedding using HSV color space and Earth Mover's Distance"""
    try:
        # Download image
        response = requests.get(img_url)
        response.raise_for_status()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Calculate 3D histogram in HSV color space
        hist = cv2.calcHist([hsv], [0, 1, 2], None, 
                           [8, 8, 8],  # Reduce bins for more general comparison
                           [0, 180, 0, 256, 0, 256])
        
        # Normalize histogram
        hist = cv2.normalize(hist, hist).flatten()
        
        # Convert to list of floats
        return hist.tolist()
        
    except Exception as e:
        logger.error(f"Error calculating color histogram: {str(e)}")
        raise 