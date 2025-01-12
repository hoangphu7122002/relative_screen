import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict
import argparse
import json
import traceback

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.db_service import DatabaseService
from src.services.gemini_service import GeminiService
from src.services.service_factory import ServiceFactory
from src.types.screen import ScreenType, SearchOptions, ScreenAnalysis

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
    logger.error("Missing required environment variables")
    sys.exit(1)

async def get_related_screens(db_service: DatabaseService, service, target_url: str, section: str, options: SearchOptions, limit: int = 5) -> tuple[List[int], List[float]]:
    """Get related screen IDs using search logic"""
    try:
        # Get target screen analysis
        target_analysis = await db_service.get_analysis_by_url(target_url)
        if not target_analysis:
            logger.error(f"Analysis not found for: {target_url}")
            return [], []
        
        # Convert string embeddings to list
        if isinstance(target_analysis['layout_embedding'], str):
            target_analysis['layout_embedding'] = eval(target_analysis['layout_embedding'])
        if isinstance(target_analysis['color_embedding'], str):
            target_analysis['color_embedding'] = eval(target_analysis['color_embedding'])
        
        target_screen = ScreenAnalysis(**target_analysis)
        
        # Get similar screens
        results = await service.search_similar(target_screen, options)
        
        # Get top N screen IDs and scores
        related_ids = []
        scores = []
        for result in results[:limit]:
            if result.screen.screen_id:
                related_ids.append(result.screen.screen_id)
                # Tính tổng điểm từ layout_score và color_score
                total_score = 0
                if hasattr(result, 'layout_score') and result.layout_score is not None:
                    total_score += result.layout_score * options.weight_layout
                if hasattr(result, 'color_score') and result.color_score is not None:
                    total_score += result.color_score * options.weight_color
                scores.append(total_score)
                
        return related_ids, scores
        
    except Exception as e:
        logger.error(f"Error getting related screens: {str(e)}")
        logger.debug(traceback.format_exc())  # Thêm log chi tiết để debug
        return [], []

async def get_related_screens_general(db_service: DatabaseService, target_url: str, section: str, limit: int = 5) -> tuple[List[int], List[float]]:
    """Get related screen IDs using general search"""
    try:
        # Get target screen analysis from screen_analysis table
        query = db_service.supabase.table('screen_analysis')\
            .select('*')\
            .eq('webp_url', target_url)\
            .eq('section', section)\
            .execute()
            
        if not query.data:
            logger.error(f"Analysis not found for webp_url: {target_url} and section: {section}")
            return [], []
            
        target_analysis = query.data[0]
        # print("===========")
        # print(target_analysis)
        # print("===========")
        # Get embedding from target analysis
        target_embedding = target_analysis.get('embedding')
        if not target_embedding:
            # Try getting layout_embedding if embedding is not found
            target_embedding = target_analysis.get('layout_embedding')
            if not target_embedding:
                logger.error("No embedding found in target analysis")
                return [], []

        # Convert string embedding to list if needed
        if isinstance(target_embedding, str):
            target_embedding = json.loads(target_embedding)

        # Search for similar sections using vector similarity
        query = db_service.supabase.rpc(
            'match_screen_embeddings',
            {
                'query_embedding': target_embedding,
                'section_type': section,
                'match_threshold': 0.5,  # Giảm ngưỡng xuống để có nhiều kết quả hơn
                'match_count': limit + 1
            }
        ).execute()

        results = query.data
        
        # Skip the first result and get screen IDs with scores
        related_ids = []
        scores = []
        for result in results[1:limit + 1]:
            screen_id = result.get('screen_id')
            if screen_id:
                related_ids.append(screen_id)
                scores.append(result.get('similarity', 0))
                
        # Log embedding info for debugging
        logger.info(f"Found embedding type: {'embedding' if target_analysis.get('embedding') else 'layout_embedding'}")
        logger.info(f"Embedding length: {len(target_embedding) if target_embedding else 0}")
        logger.info(f"Found {len(related_ids)} related screens")
                
        return related_ids, scores

    except Exception as e:
        logger.error(f"Error getting related screens (general): {str(e)}")
        logger.debug(traceback.format_exc())  # Thêm traceback để debug
        return [], []

async def update_related_screens(
    mode: str = 'specific',
    search_layout: bool = True,
    search_color: bool = True,
    weight_layout: float = 0.5,
    weight_color: float = 0.5,
    limit: int = 5
):
    """Update related screens for all records based on mode"""
    try:
        # Initialize services
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)
        
        # Create search options for specific mode
        options = SearchOptions(
            search_layout=search_layout,
            search_color=search_color,
            weight_layout=weight_layout,
            weight_color=weight_color
        )
        
        # Get records based on mode
        if mode == 'specific':
            # For specific mode, get records from relative_screen
            result = supabase.table('relative_screen')\
                .select('*')\
                .eq('screen_related_ids', [])\
                .execute()
                
            if not result.data:
                logger.info("No records to update in relative_screen")
                return
                
            # Process each record
            total = len(result.data)
            logger.info(f"Found {total} records to update")
            logger.info(f"Mode: {mode}")
            logger.info(f"Search config: layout={search_layout}, color={search_color}, "
                       f"weights=({weight_layout:.1f}, {weight_color:.1f}), limit={limit}")
            
            for idx, record in enumerate(result.data, 1):
                try:
                    logger.info(f"Processing {idx}/{total}: {record['img_url']}")
                    
                    section_type = ScreenType(record['section'])
                    service = ServiceFactory.get_service(
                        section_type,
                        gemini_service=gemini_service,
                        db_service=db_service
                    )
                    related_ids, scores = await get_related_screens(
                        db_service,
                        service,
                        record['img_url'],
                        record['section'],
                        options,
                        limit=limit
                    )
                    
                    # Update relative_screen record
                    if related_ids:
                        logger.info("Related screens found with scores:")
                        for idx, (screen_id, score) in enumerate(zip(related_ids, scores), 1):
                            logger.info(f"  {idx}. Screen ID: {screen_id}, Score: {score:.4f}")
                            
                        supabase.table('relative_screen')\
                            .update({'screen_related_ids': related_ids})\
                            .eq('id', record['id'])\
                            .execute()
                        
                        logger.info(f"✓ Updated relative_screen with {len(related_ids)} related screens")
                    else:
                        logger.warning("No related screen IDs found")
                        
                except Exception as e:
                    logger.error(f"Error processing record {record['id']}: {str(e)}")
                    continue
                    
        else:  # general mode
            # For general mode, get records from screen_analysis
            result = supabase.table('screen_analysis')\
                .select('*')\
                .eq('screen_related_ids', [])\
                .execute()
                
            if not result.data:
                logger.info("No records to update in screen_analysis")
                return
                
            # Process each record
            total = len(result.data)
            logger.info(f"Found {total} records to update")
            logger.info(f"Mode: {mode}")
            
            for idx, record in enumerate(result.data, 1):
                try:
                    logger.info(f"Processing {idx}/{total}: {record['webp_url']}")
                    
                    related_ids, scores = await get_related_screens_general(
                        db_service,
                        record['webp_url'],
                        record['section'],
                        limit=limit
                    )
                    
                    # Update screen_analysis record directly
                    if related_ids:
                        logger.info("Related screens found with scores:")
                        for idx, (screen_id, score) in enumerate(zip(related_ids, scores), 1):
                            logger.info(f"  {idx}. Screen ID: {screen_id}, Score: {score:.4f}")
                            
                        supabase.table('screen_analysis')\
                            .update({'screen_related_ids': related_ids})\
                            .eq('id', record['id'])\
                            .execute()
                            
                        logger.info(f"✓ Updated screen_analysis with {len(related_ids)} related screens")
                    else:
                        logger.warning("No related screen IDs found")
                        
                except Exception as e:
                    logger.error(f"Error processing record {record['id']}: {str(e)}")
                    continue

    except Exception as e:
        logger.error(f"Error updating related screens: {str(e)}")
        raise
        
def parse_args():
    parser = argparse.ArgumentParser(description='Update related screens for all records')
    parser.add_argument('--mode', choices=['specific', 'general'],
                       default='specific', help='Search mode to use')
    parser.add_argument('--no-layout', action='store_true',
                       help='Disable layout similarity search')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable color similarity search')
    parser.add_argument('--weight-layout', type=float, default=0.5,
                       help='Weight for layout similarity (default: 0.5)')
    parser.add_argument('--weight-color', type=float, default=0.5,
                       help='Weight for color similarity (default: 0.5)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Maximum number of related screens per record (default: 5)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    asyncio.run(update_related_screens(
        mode=args.mode,
        search_layout=not args.no_layout,
        search_color=not args.no_color,
        weight_layout=args.weight_layout,
        weight_color=args.weight_color,
        limit=args.limit
    )) 