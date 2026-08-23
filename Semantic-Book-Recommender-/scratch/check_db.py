import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Query books
res = supabase.table("books").select("id, title, thumbnail, isbn13").ilike("title", "%Atomic Habits%").execute()
print("Atomic Habits:", res.data)

res = supabase.table("books").select("id, title, thumbnail, isbn13").ilike("title", "%Great Gatsby%").execute()
print("The Great Gatsby:", res.data)
