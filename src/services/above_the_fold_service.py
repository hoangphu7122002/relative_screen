from typing import Optional
from .screen_service import ScreenService
from .gemini_service import GeminiService
from .db_service import DatabaseService
from ..types.screen import ScreenType

class AboveTheFoldService(ScreenService):
    def __init__(self, gemini_service: Optional[GeminiService] = None, db_service: Optional[DatabaseService] = None):
        super().__init__(ScreenType.ABOVE_THE_FOLD, gemini_service, db_service)

    async def analyze_layout(self, image_path: str) -> dict:
        """Analyze above the fold section layout using Gemini"""
        return await super().analyze_layout(image_path)

    async def search_similar(self, image_path: str, options=None):
        """Search for similar above the fold sections"""
        return await super().search_similar(image_path, options) 