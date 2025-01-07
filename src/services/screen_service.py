from typing import Dict, List, Optional
from ..types.screen import ScreenType, ScreenAnalysis, SearchOptions, SearchResult
from ..utils.embeddings import EmbeddingProcessor
from ..utils.color_histogram import get_color_histogram_embedding
from ..utils.similarity import calculate_cosine_similarity, calculate_histogram_similarity
from .base_service import BaseScreenService
from .gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class ScreenService(BaseScreenService):
    """Generic service for handling different screen types"""
    
    def __init__(self, screen_type: ScreenType, gemini_service: GeminiService, db_service):
        self.screen_type = screen_type
        self.gemini_service = gemini_service
        self.db_service = db_service
        self.embedding_processor = EmbeddingProcessor()
        
    async def analyze_layout(self, img_url: str) -> Dict:
        """Analyze layout using Gemini Vision API"""
        layout_data = await self.gemini_service.analyze_layout(
            img_url=img_url,
            screen_type=self.screen_type
        )
        if layout_data is None:
            raise Exception("Failed to analyze layout")
        return layout_data
    
    async def get_layout_embedding(self, layout_data: Dict) -> List[float]:
        """Get layout embedding using OpenAI"""
        return await self.embedding_processor.get_layout_embedding(layout_data)
    
    async def get_color_embedding(self, img_url: str) -> List[float]:
        """Get color histogram embedding"""
        return await get_color_histogram_embedding(img_url)
    
    async def analyzeAndStore(self, img_url: str, site_url: str) -> ScreenAnalysis:
        """Analyze and store screen data"""
        try:
            # Get layout analysis
            layout_data = await self.analyze_layout(img_url)
            
            # Get embeddings
            layout_embedding = await self.get_layout_embedding(layout_data)
            color_embedding = await self.get_color_embedding(img_url)
            
            # Create and return analysis
            return ScreenAnalysis(
                section=self.screen_type,
                site_url=site_url,
                img_url=img_url,
                layout_embedding=layout_embedding,
                color_embedding=color_embedding,
                layout_data=layout_data
            )
        except Exception as e:
            logger.error(f"Error in analyzeAndStore: {str(e)}")
            raise
    
    async def search_similar(
        self,
        target_screen: ScreenAnalysis,
        options: SearchOptions
    ) -> List[SearchResult]:
        """Search for similar screens"""
        results = []
        
        # Get all screens of same type from database
        screens = await self.db_service.get_screens_by_type(self.screen_type)
        
        for screen_data in screens:
            # Skip if this is the target screen
            if screen_data['img_url'] == target_screen.img_url:
                continue
                
            # Convert string embeddings to list
            if isinstance(screen_data['layout_embedding'], str):
                screen_data['layout_embedding'] = eval(screen_data['layout_embedding'])
            if isinstance(screen_data['color_embedding'], str):
                screen_data['color_embedding'] = eval(screen_data['color_embedding'])
            
            screen = ScreenAnalysis(**screen_data)
            final_score = 0
            layout_score = None
            color_score = None
            num_enabled_features = 0
            
            if options.search_layout:
                layout_score = calculate_cosine_similarity(
                    target_screen.layout_embedding,
                    screen.layout_embedding
                )
                final_score += layout_score
                num_enabled_features += 1
                
            if options.search_color:
                color_score = calculate_histogram_similarity(
                    target_screen.color_embedding,
                    screen.color_embedding
                )
                final_score += color_score
                num_enabled_features += 1
            
            # Calculate average score instead of weighted sum
            if num_enabled_features > 0:
                final_score = final_score / num_enabled_features
                
                # Apply weights only if both features are enabled
                if num_enabled_features == 2:
                    final_score = (layout_score * options.weight_layout + 
                                 color_score * options.weight_color)
                
            results.append(SearchResult(
                screen=screen,
                score=final_score,
                layout_score=layout_score,
                color_score=color_score
            ))
            
        return sorted(results, key=lambda x: x.score, reverse=True) 