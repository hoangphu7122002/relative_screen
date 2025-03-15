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
from src.types.screen import ScreenType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
PUBLIC_SUPABASE_URL = os.getenv('PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY, OPENAI_API_KEY]):
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

async def process_unprocessed_screens(db_service: DatabaseService, gemini_service: GeminiService, max_items: Optional[int] = None):
    """Process all unprocessed screens regardless of section"""
    try:
        # Get all unprocessed screenshots without filtering by section
        data = await db_service.get_all_unprocessed_screenshots(max_items)
        
        if not data:
            logger.info("No unprocessed screenshots found")
            return
            
        logger.info(f"Found {len(data)} unprocessed screenshots")
        
        # Process screenshots
        for idx, item in enumerate(data, 1):
            try:
                section = item["section"]
                logger.info(f"Processing {idx}/{len(data)}: {item['img_url']} (Section: {section})")
                
                service = ScreenService(
                    section=section,
                    gemini_service=gemini_service,
                    db_service=db_service
                )
                
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
        logger.error(f"Error processing unprocessed screens: {str(e)}")
        logger.debug(traceback.format_exc())

async def main(section: str, max_items: Union[int, str] = 5):
    """Main execution function"""
    try:
        # Initialize clients and services
        supabase = create_client(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)

        # Create table if needed
        if not db_service.create_screen_section_analysis_table():
            return

        if section.lower() == 'all':
            # Process all unprocessed screens without filtering by section
            await process_unprocessed_screens(
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