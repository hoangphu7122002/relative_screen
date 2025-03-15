import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
PUBLIC_SUPABASE_URL = os.getenv("PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# OpenAI configuration
openai_api_key = os.getenv("OPENAI_API_KEY")

# Gemini configuration
gemini_api_key = os.getenv("GEMINI_API_KEY") 