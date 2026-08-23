from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

# Load .env from parent directory or current directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

res = (
    supabase.table("books")
    .select("title, authors, simple_categories, description, isbn13, thumbnail")
    .not_.is_("thumbnail", "null")
    .neq("thumbnail", "cover-not-found.jpg")
    .neq("thumbnail", "")
    .limit(5)
    .execute()
)

for book in res.data:
    print(book)

