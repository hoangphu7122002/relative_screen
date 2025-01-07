import logging
from typing import Optional, List, Dict
from supabase import Client

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.storage_url = "http://127.0.0.1:54321/storage/v1/object/public/screens"

    def create_screen_section_analysis_table(self):
        """Creates the relative_screen table if it doesn't exist"""
        try:
            # Check if table exists
            try:
                self.supabase.table('relative_screen').select('id').limit(1).execute()
                logger.info("Relative screen table already exists")
                return True
            except Exception as e:
                if 'relation "relative_screen" does not exist' not in str(e):
                    raise e

            # Execute SQL to create table
            sql = """
            -- Enable vector extension if not exists
            create extension if not exists vector;

            -- Create relative_screen table
            create table relative_screen (
                id bigint primary key generated always as identity,
                screen_id bigint references screens(id),
                section text not null,
                site_url text not null,
                img_url text not null,
                layout_embedding vector(1536),
                color_embedding vector(512),
                layout_data jsonb,
                created_at timestamp with time zone default timezone('utc'::text, now()),
                updated_at timestamp with time zone default timezone('utc'::text, now())
            );

            -- Create indexes for efficient querying
            create index relative_screen_screen_id_idx on relative_screen(screen_id);
            create index relative_screen_section_idx on relative_screen(section);
            create index relative_screen_site_url_idx on relative_screen(site_url);
            create index relative_screen_layout_embedding_idx on relative_screen using ivfflat (layout_embedding vector_cosine_ops);
            create index relative_screen_color_embedding_idx on relative_screen using ivfflat (color_embedding vector_cosine_ops);
            """
            
            # Execute SQL
            self.supabase.query(sql).execute()
            logger.info("Created relative_screen table successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating relative screen table: {str(e)}")
            raise

    def get_storage_url(self, img_url: str) -> str:
        """
        Convert relative path to full storage URL
        Example:
        img_url: 'lemcal.com/20240804160759-CleanShot_2024-08-04_at_16.webp'
        returns: 'http://127.0.0.1:54321/storage/v1/object/public/screens/lemcal.com/20240804160759-CleanShot_2024-08-04_at_16.webp'
        """
        # Remove any leading slashes
        img_url = img_url.lstrip('/')
        return f"{self.storage_url}/{img_url}"

    async def get_unprocessed_screenshots(self, section: str, max_items: Optional[int] = None):
        """Get unprocessed screenshots from screens table"""
        try:
            # Get screenshots from screens table that haven't been processed in relative_screen
            query = self.supabase.table('screens')\
                .select('id, img_url, section, site_url')\
                .eq('section', section)\
                .not_.eq('is_public', False)\
                .order('date', desc=True)
            
            if max_items:
                query = query.limit(max_items)
                
            result = query.execute()
            
            if not result.data:
                return []
            
            # Format data
            formatted_data = []
            for item in result.data:
                # Check if already processed
                processed = self.supabase.table('relative_screen')\
                    .select('id')\
                    .eq('screen_id', item['id'])\
                    .execute()
                
                if not processed.data:  # Only include if not processed
                    formatted_data.append({
                        "screen_id": item['id'],
                        "img_url": self.get_storage_url(item['img_url']),
                        "original_img_url": item['img_url'],
                        "site_url": item['site_url'],
                        "section": item['section']
                    })
            
            return formatted_data

        except Exception as e:
            logger.error(f"Error getting unprocessed screenshots: {str(e)}")
            raise

    async def mark_as_processed(self, screen_id: int, analysis_data: dict):
        """Store analysis results in relative_screen table"""
        try:
            # Store original img_url, not the full URL
            if 'original_img_url' in analysis_data:
                analysis_data['img_url'] = analysis_data.pop('original_img_url')
            
            data = {
                "screen_id": screen_id,
                **analysis_data
            }
            
            result = self.supabase.table('relative_screen')\
                .insert(data)\
                .execute()
                
            logger.info(f"Stored analysis for screen {screen_id}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
            raise

    async def get_screens_by_type(self, section: str) -> List[Dict]:
        """Get all processed screens of a specific type"""
        try:
            result = self.supabase.table('relative_screen')\
                .select('*')\
                .eq('section', section)\
                .execute()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting screens by type: {str(e)}")
            raise

    async def get_analysis_by_url(self, img_url: str):
        """Get analysis data by image URL"""
        try:
            # If full URL is provided, extract the relative path
            if img_url.startswith(self.storage_url):
                img_url = img_url.replace(f"{self.storage_url}/", "")

            result = self.supabase.table('relative_screen')\
                .select('*')\
                .eq('img_url', img_url)\
                .single()\
                .execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting analysis by URL: {str(e)}")
            raise 