import os
import json
import logging
from typing import List, Dict
from openai import OpenAI

logger = logging.getLogger(__name__)

class EmbeddingProcessor:
    """Handles creation of embeddings using OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding from text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    def _format_json_string(self, layout_data: Dict) -> str:
        """Convert layout JSON to formatted string"""
        try:
            return json.dumps(layout_data, indent=2)
        except Exception as e:
            logger.error(f"Error formatting JSON string: {str(e)}")
            return str(layout_data)

    async def get_layout_embedding(self, layout_data: Dict) -> List[float]:
        """Create embedding for layout data using OpenAI API"""
        # Convert layout data to JSON string
        layout_text = self._format_json_string(layout_data)
        
        # Create embedding
        return self._create_embedding(layout_text) 