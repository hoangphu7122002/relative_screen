import os
import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
from ..config.prompts import SCREEN_PROMPTS
from ..types.screen import ScreenType

logger = logging.getLogger(__name__)

class GeminiService:
    """Handles image analysis using Gemini API"""
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Downloads image and returns PIL Image"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None

    async def analyze_layout(self, img_url: str, screen_type: ScreenType) -> Optional[Dict]:
        """Analyzes an image using Gemini API"""
        try:
            # Get prompt for screen type
            prompt = SCREEN_PROMPTS.get(screen_type)
            if not prompt:
                raise ValueError(f"No prompt defined for screen type: {screen_type}")

            # Download image
            image = self._download_image(img_url)
            if not image:
                raise Exception(f"Failed to download image from {img_url}")
            
            # Generate response
            response = self.model.generate_content([prompt, image])
            json_str = response.text.strip('```json').strip('```').strip()
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None 