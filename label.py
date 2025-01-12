import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client
from typing import Optional, Union
import argparse
import traceback

from src.services.db_service import DatabaseService
from src.services.gemini_service import GeminiService
from src.services.screen_service import ScreenService

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

async def process_section(section: str, db_service: DatabaseService, gemini_service: GeminiService, max_items: Optional[int] = None):
    """Process a single section"""
    try:
        # Initialize screen service directly
        service = ScreenService(
            section=section,  # Pass section as string directly
            gemini_service=gemini_service,
            db_service=db_service
        )

        # Get unprocessed screenshots
        data = await db_service.get_unprocessed_screenshots(section, max_items)
        
        if not data:
            logger.info(f"No unprocessed screenshots found for section: {section}")
            return
            
        logger.info(f"Found {len(data)} unprocessed screenshots for section: {section}")
        
        # Process screenshots
        for idx, item in enumerate(data, 1):
            try:
                logger.info(f"Processing {idx}/{len(data)}: {item['img_url']}")
                analysis = await service.analyzeAndStore(
                    img_url=item["img_url"],
                    site_url=item["site_url"]
                )
                if analysis:
                    await db_service.mark_as_processed(
                        item["screen_id"],
                        {
                            "section": section,
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
        logger.error(f"Error processing section {section}: {str(e)}")
        logger.debug(traceback.format_exc())

async def main(section: str, max_items: Union[int, str] = 5):
    """Main execution function"""
    try:
        # Initialize clients and services
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)

        # Create table if needed
        if not db_service.create_screen_section_analysis_table():
            return

        if section.lower() == 'all':
            # Get all unique sections from database
            sections = await db_service.get_all_sections()
            logger.info(f"Found {len(sections)} sections to process: {', '.join(sections)}")
            
            # Process each section
            for section_name in sections:
                logger.info(f"\n{'='*50}")
                logger.info(f"Processing section: {section_name}")
                logger.info(f"{'='*50}")
                await process_section(
                    section_name,
                    db_service,
                    gemini_service,
                    max_items
                )
        else:
            # Process specific section
            await process_section(
                section,
                db_service,
                gemini_service,
                max_items
            )

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Screenshot analysis and labeling tool')
    parser.add_argument('--section', type=str, required=True,
                       help='Section type to process (any section name or "all")')
    parser.add_argument('--max-items', type=str, default='all',
                       help='Maximum number of screenshots to analyze (default: all)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    import asyncio
    asyncio.run(main(section=args.section, max_items=args.max_items)) 