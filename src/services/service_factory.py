from typing import Optional
from .screen_service import ScreenService
from ..types.screen import ScreenType

class ServiceFactory:
    _services = {}

    @classmethod
    def get_service(cls, section_type: ScreenType, gemini_service=None, db_service=None) -> ScreenService:
        """Get service instance based on section type"""
        if section_type not in cls._services:
            cls._services[section_type] = ScreenService(
                section=section_type,
                gemini_service=gemini_service,
                db_service=db_service
            )
        
        return cls._services[section_type] 