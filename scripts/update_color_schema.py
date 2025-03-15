import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

PUBLIC_SUPABASE_URL = os.getenv('PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not all([PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY]):
    logger.error("Missing required environment variables")
    sys.exit(1)

def update_color_embedding_schema():
    """Update color_embedding column in relative_screen table"""
    try:
        # Initialize Supabase client
        supabase = create_client(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Execute SQL statements one by one
        # sql = """
        # -- First, drop the existing color_embedding column and its index
        # DROP INDEX IF EXISTS relative_screen_color_embedding_idx;
        # ALTER TABLE relative_screen DROP COLUMN IF EXISTS color_embedding;
        
        # -- Then add the new color_embedding column with correct dimensions (8*8*8 = 512)
        # ALTER TABLE relative_screen ADD COLUMN color_embedding vector(512);
        
        # -- Create new index
        # CREATE INDEX relative_screen_color_embedding_idx 
        # ON relative_screen 
        # USING ivfflat (color_embedding vector_cosine_ops);
        # """
        try:
            # Drop index if exists
            supabase.table('relative_screen')\
                .alter('DROP INDEX IF EXISTS relative_screen_color_embedding_idx')\
                .execute()
            logger.info("Dropped old index")
            
            # Create new column with updated dimensions
            supabase.table('relative_screen')\
                .alter('ALTER TABLE relative_screen DROP COLUMN IF EXISTS color_embedding')\
                .execute()
            logger.info("Dropped old column")
            
            # Add new column for HSV histogram (8x8x8 = 512)
            supabase.table('relative_screen')\
                .alter('ALTER TABLE relative_screen ADD COLUMN color_embedding vector(512)')\
                .execute()
            logger.info("Added new column")
            
            # Create optimized index for similarity search
            supabase.table('relative_screen')\
                .alter("""
                    CREATE INDEX relative_screen_color_embedding_idx 
                    ON relative_screen 
                    USING ivfflat (color_embedding vector_cosine_ops)
                """)\
                .execute()
            logger.info("Created new index")
            
            logger.info("Successfully updated color_embedding schema")
            return True
            
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating schema: {str(e)}")
        return False

if __name__ == "__main__":
    update_color_embedding_schema() 