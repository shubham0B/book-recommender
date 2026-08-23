import pandas as pd
import numpy as np
import os
import re
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

csv_path = "book.csv"
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found")
    exit(1)

print(f"Loading {csv_path}...")
df = pd.read_csv(csv_path)

# Drop unnamed index column if exists
if df.columns[0] == "" or "Unnamed" in df.columns[0]:
    df = df.iloc[:, 1:]

print(f"Total books found in CSV: {len(df)}")

# Fill missing values
df["title"] = df["title"].fillna("Unknown Title")
df["authors"] = df["authors"].fillna("Unknown Author")
df["description"] = df["description"].fillna("")
df["image_url"] = df["image_url"].fillna("cover-not-found.jpg")

# Filter out books with completely empty descriptions
df = df[df["description"].str.strip() != ""].reset_index(drop=True)
print(f"Books with valid descriptions: {len(df)}")

# Generate embeddings
print("Initializing embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

descriptions = df["description"].tolist()
print(f"Generating embeddings for {len(descriptions)} books... (this may take a few minutes)")
embeddings = embeddings_model.embed_documents(descriptions)

print("Uploading books and embeddings to Supabase in batches...")
batch_size = 50

for i in range(0, len(df), batch_size):
    batch = df.iloc[i : i + batch_size]
    batch_embeddings = embeddings[i : i + batch_size]

    records = []
    for j, (_, row) in enumerate(batch.iterrows()):
        # Try to parse book_id or isbn
        book_id = None
        if "book_id" in row and not pd.isna(row["book_id"]):
            try:
                book_id = int(row["book_id"])
            except:
                pass

        records.append({
            "isbn13": book_id,
            "title": str(row["title"]),
            "authors": str(row["authors"]),
            "description": str(row["description"]),
            "thumbnail": str(row["image_url"]),
            "simple_categories": "Fiction" if "Fiction" in str(row.get("categories", "")) else "General",
            "joy": 0.0,
            "surprise": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "sadness": 0.0,
            "embedding": batch_embeddings[j],
        })

    try:
        supabase.table("books").insert(records).execute()
        print(f"Uploaded {min(i + batch_size, len(df))}/{len(df)} books...")
    except Exception as e:
        print(f"Error uploading batch {i} - {i + batch_size}: {e}")

print("Import successfully completed! ✅")
