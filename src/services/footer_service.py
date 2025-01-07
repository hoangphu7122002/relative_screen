from .screen_service import ScreenService
from ..types.screen import ScreenType
from .gemini_service import GeminiService
from .db_service import DatabaseService

class FooterService(ScreenService):
    def __init__(self, gemini_service: GeminiService, db_service: DatabaseService):
        super().__init__(ScreenType.FOOTER, gemini_service, db_service) 