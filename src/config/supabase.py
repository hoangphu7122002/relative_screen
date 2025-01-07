import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# OpenAI configuration
openai_api_key = os.getenv("OPENAI_API_KEY")

# Gemini configuration
gemini_api_key = os.getenv("GEMINI_API_KEY") 