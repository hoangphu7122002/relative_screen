from abc import ABC, abstractmethod
from typing import Dict, List
from ..types.screen import ScreenAnalysis, SearchOptions, SearchResult

class BaseScreenService(ABC):
    """Base class for all screen type services"""
    
    @abstractmethod
    async def analyze_layout(self, img_url: str) -> Dict:
        """Analyze layout using Gemini Vision API"""
        pass
    
    @abstractmethod
    async def get_layout_embedding(self, layout_data: Dict) -> List[float]:
        """Get layout embedding using OpenAI"""
        pass
    
    @abstractmethod
    async def get_color_embedding(self, img_url: str) -> List[float]:
        """Get color histogram embedding"""
        pass
    
    @abstractmethod
    async def analyzeAndStore(self, img_url: str) -> ScreenAnalysis:
        """Analyze and store screen data"""
        pass
    
    @abstractmethod
    async def search_similar(
        self, 
        target_screen: ScreenAnalysis,
        options: SearchOptions
    ) -> List[SearchResult]:
        """Search for similar screens"""
        pass 