# Screen Analysis Tools

Tools for analyzing and searching similar website sections (footer, above the fold, testimonials, etc).

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key
```

## Labeling Screenshots

The labeling script analyzes screenshots and stores their layout and color embeddings.

Usage:
```bash
# Process specific section type
python label.py --section "footer" --max-items 10
python label.py --section "above the fold" --max-items 5
python label.py --section "testimonials" --max-items 5

# Process all unprocessed screenshots for a section
python label.py --section "footer" --max-items all
```

Parameters:
- `--section`: Type of section to process (footer, above the fold, testimonials)
- `--max-items`: Number of screenshots to process (default: 5, use "all" for all screenshots)

## Searching Similar Sections

Search for similar sections based on layout and color patterns.

Usage:
```bash
# Basic search with default weights
python search.py --target_url example.com/footer.webp --section "footer"

# Search above the fold sections
python search.py --target_url example.com/hero.webp --section "above the fold"

# Search testimonials sections
python search.py --target_url example.com/testimonials.webp --section "testimonials"

# Search with layout only
python search.py --target_url example.com/footer.webp --section "footer" --no-color

# Search with color only
python search.py --target_url example.com/footer.webp --section "footer" --no-layout

# Adjust weights and limit results
python search.py --target_url example.com/footer.webp --section "footer" --weight-layout 0.7 --weight-color 0.3 --limit 10
```

Parameters:
- `target_url`: URL of the target screenshot
- `section`: Type of section to search (footer, above the fold, testimonials)
- `--no-layout`: Disable layout similarity search
- `--no-color`: Disable color similarity search
- `--weight-layout`: Weight for layout similarity (default: 0.7)
- `--weight-color`: Weight for color similarity (default: 0.3)
- `--limit`: Maximum number of results to show (default: 5)

## Project Structure
```
screen_relative/
├── src/
│   ├── config/
│   │   ├── prompts.py         # Analysis prompts for different screen types
│   │   └── supabase.py        # Supabase configuration
│   ├── types/
│   │   └── screen.py          # Data models and types
│   ├── utils/
│   │   ├── embeddings.py      # OpenAI embedding utilities
│   │   ├── color_histogram.py # Color analysis utilities
│   │   └── similarity.py      # Similarity calculation functions
│   └── services/
│       ├── base_service.py    # Base service interface
│       ├── screen_service.py  # Generic screen analysis service
│       ├── footer_service.py  # Footer-specific service
│       ├── above_the_fold_service.py # Above the fold service
│       ├── testimonials_service.py   # Testimonials service
│       ├── service_factory.py # Service factory for different sections
│       ├── db_service.py      # Database operations
│       └── gemini_service.py  # Gemini API service
├── requirements.txt           # Project dependencies
├── label.py                  # Screenshot labeling script
└── search.py                 # Similar section search script
``` 