# Screen Analysis Tools

Tools for analyzing and searching similar website footer layouts.

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

The labeling script analyzes footer screenshots and stores their layout and color embeddings.

Usage:
```bash
# Process 5 screenshots (default)
python label.py

# Process specific number of screenshots
python label.py --max-items 10

# Process all unprocessed screenshots
python label.py --max-items all
```

## Searching Similar Footers

Search for similar footers based on layout and color patterns.

Usage:
```bash
# Basic search with default weights
python search.py --target_url example.com/footer.webp

# Search with layout only
python search.py --target_url example.com/footer.webp --no-color

# Search with color only
python search.py --target_url example.com/footer.webp --no-layout

# Adjust weights and limit results
python search.py --target_url example.com/footer.webp --weight-layout 0.7 --weight-color 0.3 --limit 10
```

Parameters:
- `target_url`: URL of the target footer screenshot
- `--no-layout`: Disable layout similarity search
- `--no-color`: Disable color similarity search
- `--weight-layout`: Weight for layout similarity (default: 0.6)
- `--weight-color`: Weight for color similarity (default: 0.4)
- `--limit`: Maximum number of results to show (default: 5)

## Updating Color Embeddings

If you need to update the color embeddings:

1. Update schema:
```bash
python scripts/update_color_schema.py
```

2. Update embeddings:
```bash
# Update all records
python scripts/update_color_embeddings.py

# Update specific number of records
python scripts/update_color_embeddings.py --max-items 10
```

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
│       ├── db_service.py      # Database operations
│       └── gemini_service.py  # Gemini API service
├── scripts/
│   ├── update_color_schema.py    # Update color embedding schema
│   └── update_color_embeddings.py # Update color embeddings
├── requirements.txt              # Project dependencies
├── label.py                     # Screenshot labeling script
└── search.py                    # Similar footer search script
``` 