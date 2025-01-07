import os
import sys
import json
import logging
from dotenv import load_dotenv
from supabase import create_client
from typing import Optional
import argparse
import traceback

from src.services.footer_service import FooterService
from src.types.screen import SearchOptions, ScreenAnalysis
from src.services.db_service import DatabaseService
from src.services.gemini_service import GeminiService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY]):
    logger.error("Missing required environment variables. Please check .env file")
    sys.exit(1)

async def search_similar_footers(
    db_service: DatabaseService,
    footer_service: FooterService,
    target_url: str,
    search_layout: bool = True,
    search_color: bool = True,
    weight_layout: float = 0.5,
    weight_color: float = 0.5,
    limit: int = 5
):
    """Search for similar footers"""
    try:
        # Get target screen analysis
        target_analysis = await db_service.get_analysis_by_url(target_url)
        if not target_analysis:
            logger.error(f"Analysis not found for: {target_url}")
            return
        
        # Convert string embeddings to list
        if isinstance(target_analysis['layout_embedding'], str):
            target_analysis['layout_embedding'] = eval(target_analysis['layout_embedding'])
        if isinstance(target_analysis['color_embedding'], str):
            target_analysis['color_embedding'] = eval(target_analysis['color_embedding'])
        
        target_screen = ScreenAnalysis(**target_analysis)
        
        # Search options
        options = SearchOptions(
            search_layout=search_layout,
            search_color=search_color,
            weight_layout=weight_layout,
            weight_color=weight_color
        )
        
        # Get similar screens
        results = await footer_service.search_similar(target_screen, options)
        
        # Print results
        logger.info(f"\nResults for {target_url}:")
        logger.info("-" * 50)
        
        for idx, result in enumerate(results[:limit], 1):
            # Convert relative path to full URL for display
            img_url = db_service.get_storage_url(result.screen.img_url)
            logger.info(f"\n{idx}. {img_url}")
            logger.info(f"Total Score: {result.score:.3f}")
            if result.layout_score:
                logger.info(f"Layout Score: {result.layout_score:.3f}")
            if result.color_score:
                logger.info(f"Color Score: {result.color_score:.3f}")

    except Exception as e:
        logger.error(f"Error searching similar footers: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

async def main(
    target_url: str,
    search_layout: bool = True,
    search_color: bool = True,
    weight_layout: float = 0.6,
    weight_color: float = 0.4,
    limit: int = 5
):
    """Main execution function"""
    try:
        # Initialize clients
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Initialize services
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)
        footer_service = FooterService(gemini_service=gemini_service, db_service=db_service)
        
        # Search
        await search_similar_footers(
            db_service,
            footer_service,
            target_url=target_url,
            search_layout=search_layout,
            search_color=search_color,
            weight_layout=weight_layout,
            weight_color=weight_color,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Footer similarity search tool')
    parser.add_argument('--target_url', help='URL of the target footer screenshot')
    parser.add_argument('--no-layout', action='store_true',
                       help='Disable layout similarity search')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable color similarity search')
    parser.add_argument('--weight-layout', type=float, default=0.7,
                       help='Weight for layout similarity (default: 0.7)')
    parser.add_argument('--weight-color', type=float, default=0.3,
                       help='Weight for color similarity (default: 0.3)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Maximum number of results to show (default: 5)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    import asyncio
    asyncio.run(main(
        target_url=args.target_url,
        search_layout=not args.no_layout,
        search_color=not args.no_color,
        weight_layout=args.weight_layout,
        weight_color=args.weight_color,
        limit=args.limit
    )) 