import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client
import asyncio
from typing import Optional, Union
import argparse

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.color_histogram import get_color_histogram_embedding
from src.services.db_service import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    logger.error("Missing required environment variables")
    sys.exit(1)

async def update_color_embeddings(max_items: Union[int, str] = 'all'):
    """Update color embeddings for all records"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db_service = DatabaseService(supabase)
        
        # Get all records
        query = supabase.table('relative_screen').select('id, img_url')
        if max_items != 'all':
            query = query.limit(int(max_items))
        
        result = query.execute()
        records = result.data
        
        if not records:
            logger.info("No records found to update")
            return
            
        logger.info(f"Found {len(records)} records to update")
        
        # Process each record
        for idx, record in enumerate(records, 1):
            try:
                # Get full image URL
                img_url = db_service.get_storage_url(record['img_url'])
                
                # Calculate new color embedding
                color_embedding = await get_color_histogram_embedding(img_url)
                
                # Update record
                supabase.table('relative_screen')\
                    .update({'color_embedding': color_embedding})\
                    .eq('id', record['id'])\
                    .execute()
                    
                logger.info(f"Updated {idx}/{len(records)}: {record['img_url']}")
                
            except Exception as e:
                logger.error(f"Error processing record {record['id']}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error updating color embeddings: {str(e)}")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Update color embeddings for relative_screen records')
    parser.add_argument('--max-items', type=str, default='all',
                       help='Maximum number of records to update (default: all)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(update_color_embeddings(max_items=args.max_items)) 