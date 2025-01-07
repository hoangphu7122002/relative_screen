import os
import sys
import logging
import asyncio
import argparse
from dotenv import load_dotenv
from supabase import create_client

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.db_service import DatabaseService
from src.utils.embeddings import EmbeddingProcessor
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
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    logger.error("Missing required environment variables")
    sys.exit(1)

async def update_above_fold_embeddings(
    db_service: DatabaseService,
    embedding_processor: EmbeddingProcessor,
    max_items: int = None
):
    """Update layout embeddings for above the fold sections"""
    try:
        # Get all above the fold analyses
        analyses = await db_service.get_analyses_by_type(
            section_type=ScreenType.ABOVE_THE_FOLD,
            limit=max_items
        )
        
        if not analyses:
            logger.info("No above the fold analyses found")
            return
            
        logger.info(f"Found {len(analyses)} above the fold analyses to update")
        
        # Update each analysis
        for idx, analysis in enumerate(analyses, 1):
            try:
                # Get new embedding for existing layout data
                layout_data = analysis['layout_data']
                new_embedding = await embedding_processor.get_layout_embedding(layout_data)
                
                # Update in database
                await db_service.update_analysis_embedding(
                    analysis_id=analysis['id'],
                    layout_embedding=new_embedding
                )
                
                logger.info(f"✓ Updated embedding for analysis {idx}/{len(analyses)}: {analysis['site_url']}")
                
            except Exception as e:
                logger.error(f"✗ Error updating analysis {analysis['id']}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error updating above fold embeddings: {str(e)}")
        raise

async def main(max_items: int = None):
    """Main execution function"""
    try:
        # Initialize services
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db_service = DatabaseService(supabase)
        embedding_processor = EmbeddingProcessor()
        
        # Update embeddings
        await update_above_fold_embeddings(
            db_service=db_service,
            embedding_processor=embedding_processor,
            max_items=max_items
        )
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Update layout embeddings for above the fold sections'
    )
    parser.add_argument('--max-items', type=int,
                       help='Maximum number of items to update (optional)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(max_items=args.max_items)) 