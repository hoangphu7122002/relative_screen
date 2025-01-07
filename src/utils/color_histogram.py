import cv2
import numpy as np
import requests
from typing import List
from io import BytesIO

async def get_color_histogram_embedding(img_url: str) -> List[float]:
    """
    Tính toán color histogram embedding từ ảnh URL.
    Sử dụng 256 bins cho mỗi kênh màu RGB.
    """
    # Tải ảnh từ URL
    response = requests.get(img_url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # Chuyển sang RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Tính histogram cho mỗi kênh màu
    histograms = []
    for i in range(3):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256])
        # Normalize histogram
        hist = cv2.normalize(hist, hist).flatten()
        histograms.extend(hist)
    
    # Kết hợp 3 histogram thành 1 vector (768 chiều)
    return np.array(histograms).tolist() 