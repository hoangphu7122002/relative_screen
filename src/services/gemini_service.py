import os
import logging
from typing import Optional
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
        """Downloads image and returns PIL Image object"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None

    def _prepare_image(self, image: Image.Image) -> bytes:
        """Optimize image size and convert to bytes"""
        try:
            # Resize image
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Error preparing image: {str(e)}")
            raise

    async def analyze_layout(self, img_url: str, screen_type: ScreenType) -> Optional[str]:
        """Analyzes an image using Gemini API and returns HTML string"""
        try:
            # Get prompt for screen type
            prompt = SCREEN_PROMPTS.get(screen_type)
            if not prompt:
                raise ValueError(f"No prompt defined for screen type: {screen_type}")

            # Download and prepare image
            image = self._download_image(img_url)
            if not image:
                raise Exception(f"Failed to download image from {img_url}")
                
            # Optimize image
            image_bytes = self._prepare_image(image)
            
            # Generate response
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ])
            
            # Log raw response for debugging
            logger.debug(f"Raw response: {response.text}")
            
            # Extract HTML from response
            text = response.text.strip()
            
            # Find HTML block in markdown code blocks if present
            if "```html" in text:
                html_str = text.split("```html")[1].split("```")[0].strip()
            elif "```" in text:
                html_str = text.split("```")[1].strip()
            else:
                html_str = text
                
            if not html_str or "<html" not in html_str:
                raise ValueError("Response does not contain valid HTML")
                
            return html_str
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None 