import os
import sys
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client
from typing import Optional, Union
import argparse
import traceback

from src.services.footer_service import FooterService
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY, OPENAI_API_KEY]):
    logger.error("Missing required environment variables. Please check .env file")
    sys.exit(1)

async def main(max_items: Union[int, str] = 5):
    """Main execution function"""
    try:
        # Initialize clients
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Initialize services
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)
        footer_service = FooterService(gemini_service=gemini_service, db_service=db_service)
        
        # Create table if needed
        if not db_service.create_screen_section_analysis_table():
            return
        
        # Get unprocessed screenshots
        data = await db_service.get_unprocessed_screenshots('footer', None if max_items == 'all' else max_items)
        
        if not data:
            logger.info("No unprocessed screenshots found")
            return
            
        logger.info(f"Found {len(data)} unprocessed screenshots")
        
        # Process screenshots
        for idx, item in enumerate(data, 1):
            try:
                logger.info(f"Processing {idx}/{len(data)}: {item['img_url']}")
                analysis = await footer_service.analyzeAndStore(
                    img_url=item["img_url"],
                    site_url=item["site_url"]
                )
                if analysis:  # Only store if analysis was successful
                    await db_service.mark_as_processed(
                        item["screen_id"],
                        {
                            "section": "footer",
                            "site_url": item["site_url"],
                            "img_url": item["original_img_url"],
                            "layout_embedding": analysis.layout_embedding,
                            "color_embedding": analysis.color_embedding,
                            "layout_data": analysis.layout_data
                        }
                    )
                    logger.info(f"✓ Processed {item['original_img_url']}")
                else:
                    logger.error(f"✗ Failed to analyze {item['original_img_url']}")
            except Exception as e:
                logger.error(f"✗ Error processing {item['original_img_url']}: {str(e)}")
                logger.debug(traceback.format_exc())

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Footer screenshot analysis and labeling tool')
    parser.add_argument('--max-items', type=str, default='5',
                       help='Maximum number of screenshots to analyze (default: 5, use "all" for all screenshots)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    # Convert max_items to int if it's not 'all'
    max_items = args.max_items if args.max_items == 'all' else int(args.max_items)
    import asyncio
    asyncio.run(main(max_items=max_items)) 