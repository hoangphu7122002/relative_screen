import os
import sys
import json
import logging
from dotenv import load_dotenv
from supabase import create_client
from typing import Optional
import argparse
import traceback

from src.types.screen import SearchOptions, ScreenAnalysis
from src.services.db_service import DatabaseService
from src.services.gemini_service import GeminiService
from src.services.service_factory import ServiceFactory
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

if not all([PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY]):
    logger.error("Missing required environment variables. Please check .env file")
    sys.exit(1)

async def search_similar_sections(
    db_service: DatabaseService,
    service,
    target_url: str,
    section: str,
    search_layout: bool = True,
    search_color: bool = True,
    weight_layout: float = 0.5,
    weight_color: float = 0.5,
    limit: int = 5
):
    """Search for similar sections"""
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
        results = await service.search_similar(target_screen, options)
        
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
        logger.error(f"Error searching similar sections: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

async def search_similar_sections_general(
    db_service: DatabaseService,
    target_url: str,
    section: str,
    limit: int = 5
):
    """Search for similar sections using screen analysis embeddings"""
    try:
        # Get target screen analysis from screen_analysis table
        query = db_service.supabase.table('screen_analysis')\
            .select('*')\
            .eq('webp_url', target_url)\
            .eq('section', section)\
            .execute()
            
        if not query.data:
            logger.error(f"Analysis not found for webp_url: {target_url} and section: {section}")
            return
            
        target_analysis = query.data[0]
        
        # Get embedding from target analysis
        target_embedding = target_analysis.get('embedding')
        if not target_embedding:
            logger.error("No embedding found in target analysis")
            return

        # Convert string embedding to list if needed
        if isinstance(target_embedding, str):
            target_embedding = json.loads(target_embedding)

        # Search for similar sections using vector similarity
        query = db_service.supabase.rpc(
            'match_screen_embeddings',
            {
                'query_embedding': target_embedding,
                'section_type': section,
                'match_threshold': 0.7,
                'match_count': limit + 1  # Get one extra to skip the first match
            }
        ).execute()

        results = query.data

        # Print target URL
        storage_url = db_service.get_storage_url(target_url)
        logger.info(f"\nSearching similar sections for:")
        logger.info(f"URL: {storage_url}")
        logger.info(f"Section: {section}")
        logger.info("-" * 50)
        
        # Skip the first result (which should be the target URL) and show the rest
        for idx, result in enumerate(results[1:limit + 1], 1):
            similarity_score = result.get('similarity')
            result_url = result.get('webp_url')
            storage_url = db_service.get_storage_url(result_url)
            logger.info(f"\n{idx}. {storage_url}")
            logger.info(f"Similarity Score: {similarity_score:.3f}")

    except Exception as e:
        logger.error(f"Error searching similar sections: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

async def main(
    target_url: str,
    section: str,
    search_layout: bool = True,
    search_color: bool = True,
    weight_layout: float = 0.6,
    weight_color: float = 0.4,
    limit: int = 5,
    mode: str = 'specific'  # Add mode parameter
):
    """Main execution function"""
    try:
        # Initialize clients
        supabase = create_client(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Initialize services
        db_service = DatabaseService(supabase)
        gemini_service = GeminiService(GEMINI_API_KEY)
        
        if mode == 'general':
            # Use general search
            await search_similar_sections_general(
                db_service,
                target_url=target_url,
                section=section,
                limit=limit
            )
        else:
            # Use specific search (original implementation)
            try:
                section_type = ScreenType(section)
                service = ServiceFactory.get_service(
                    section_type,
                    gemini_service=gemini_service,
                    db_service=db_service
                )
            except ValueError as e:
                logger.error(f"Invalid section type: {section}")
                return
            
            await search_similar_sections(
                db_service,
                service,
                target_url=target_url,
                section=section,
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
    parser = argparse.ArgumentParser(description='Section similarity search tool')
    parser.add_argument('--target_url', required=True,
                       help='URL of the target screenshot')
    parser.add_argument('--section', type=str, required=True,
                       help='Section type to search (footer, above the fold, etc)')
    parser.add_argument('--mode', choices=['specific', 'general'],
                       default='specific', help='Search mode to use')
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
        section=args.section,
        search_layout=not args.no_layout,
        search_color=not args.no_color,
        weight_layout=args.weight_layout,
        weight_color=args.weight_color,
        limit=args.limit,
        mode=args.mode
    ))