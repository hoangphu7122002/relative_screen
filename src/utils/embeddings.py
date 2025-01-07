import os
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

    def format_layout_data(self, layout_data: Dict) -> str:
        """Convert layout JSON to text format for effective embedding"""
        text_parts = []
        
        # Format rows
        for row in layout_data.get("rows", []):
            row_index = row.get("rowIndex")
            text_parts.append(f"Row {row_index}:")
            
            # Format content in each row
            for content in row.get("content", []):
                position = content.get("position", "")
                name = content.get("name", "")
                text = content.get("text", "")
                title = content.get("title", "")
                links = content.get("links", [])
                
                if text:
                    text_parts.append(f"  {position} {name}: {text}")
                if title:
                    text_parts.append(f"  {position} {name} title: {title}")
                if links:
                    text_parts.append(f"  {position} {name} links: {', '.join(links)}")
        
        return "\n".join(text_parts)

    async def get_layout_embedding(self, layout_data: Dict) -> List[float]:
        """Create embedding for layout data using OpenAI API"""
        # Convert layout data to text format
        layout_text = self.format_layout_data(layout_data)
        
        # Create embedding
        return self._create_embedding(layout_text) 