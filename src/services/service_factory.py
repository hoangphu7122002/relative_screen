from typing import Optional
from .footer_service import FooterService
from .above_the_fold_service import AboveTheFoldService
from .screen_service import ScreenService
from ..types.screen import ScreenType

class ServiceFactory:
    _services = {}

    @classmethod
    def get_service(cls, section_type: ScreenType, gemini_service=None, db_service=None) -> ScreenService:
        """Get service instance based on section type"""
        if section_type not in cls._services:
            if section_type == ScreenType.FOOTER:
                cls._services[section_type] = FooterService(
                    gemini_service=gemini_service,
                    db_service=db_service
                )
            elif section_type == ScreenType.ABOVE_THE_FOLD:
                cls._services[section_type] = AboveTheFoldService(
                    gemini_service=gemini_service,
                    db_service=db_service
                )
            else:
                raise ValueError(f"Unsupported section type: {section_type}")
        
        return cls._services[section_type] 