from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class ScreenType(str, Enum):
    FOOTER = "footer"
    ABOVE_THE_FOLD = "above the fold"
    TESTIMONIALS = "testimonials"
    FEATURES = "features"
    MORE_FEATURES = "more features"
    HOW_IT_WORKS = "how it works"
    PRICING = "pricing"
    COMPLEX_PRICING = "complex pricing"
    FAQS = "FAQs"
    LAST_CTA = "Last CTA"
    BLOG = "Blog"
    

class ScreenAnalysis(BaseModel):
    id: Optional[int] = None
    screen_id: Optional[int] = None
    section: ScreenType
    site_url: str
    img_url: str
    layout_embedding: List[float]
    color_embedding: List[float]
    layout_data: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SearchOptions(BaseModel):
    search_layout: bool = True
    search_color: bool = True
    weight_layout: float = 0.5
    weight_color: float = 0.5

class SearchResult(BaseModel):
    screen: ScreenAnalysis
    score: float
    layout_score: Optional[float]
    color_score: Optional[float] 