import pandas as pd
import numpy as np
import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

csv_path = r"C:\Users\sharm\Downloads\archive\book.csv"
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found")
    sys.exit(1)

print(f"Loading books from {csv_path}...", flush=True)
df = pd.read_csv(csv_path)

# Drop unnamed index column if exists
if df.columns[0] == "" or "Unnamed" in df.columns[0]:
    df = df.iloc[:, 1:]

print(f"Total books in file: {len(df)}", flush=True)

# Fill missing values
df["title"] = df["title"].fillna("Unknown Title")
df["authors"] = df["authors"].fillna("Unknown Author")
df["description"] = df["description"].fillna("")
df["image_url"] = df["image_url"].fillna("cover-not-found.jpg")

# Filter out books with empty descriptions
df = df[df["description"].str.strip() != ""].reset_index(drop=True)
print(f"Books with valid descriptions: {len(df)}", flush=True)

# Check existing titles in Supabase to avoid exact duplicate inserts
print("Checking existing titles in Supabase...", flush=True)
existing_titles_data = supabase.table("books").select("title").execute().data
existing_titles = set(row["title"].strip().lower() for row in existing_titles_data if row.get("title"))
print(f"Found {len(existing_titles)} existing books in Supabase.", flush=True)

# Filter out duplicates
df["title_clean"] = df["title"].str.strip().str.lower()
df = df[~df["title_clean"].isin(existing_titles)].reset_index(drop=True)
print(f"New unique books to import: {len(df)}", flush=True)

if len(df) == 0:
    print("All books from this file are already imported in Supabase! ✅", flush=True)
    sys.exit(0)

# Initialize embedding model
print("Initializing sentence-transformers embedding model...", flush=True)
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

descriptions = df["description"].tolist()
print(f"Generating embeddings for {len(descriptions)} books...", flush=True)
embeddings = embeddings_model.embed_documents(descriptions)

print("Uploading to Supabase in batches of 50...", flush=True)
batch_size = 50
total_uploaded = 0

for i in range(0, len(df), batch_size):
    batch = df.iloc[i : i + batch_size]
    batch_embeddings = embeddings[i : i + batch_size]

    records = []
    for j, (_, row) in enumerate(batch.iterrows()):
        isbn_val = None
        if "book_id" in row and not pd.isna(row["book_id"]):
            try:
                isbn_val = int(row["book_id"])
            except:
                isbn_val = None

        records.append({
            "isbn13": isbn_val,
            "title": str(row["title"]).strip(),
            "authors": str(row["authors"]).strip(),
            "description": str(row["description"]).strip(),
            "thumbnail": str(row["image_url"]).strip(),
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
        total_uploaded += len(records)
        print(f"Progress: {total_uploaded}/{len(df)} books uploaded...", flush=True)
    except Exception as e:
        print(f"Error uploading batch starting at index {i}: {e}", flush=True)

print(f"Successfully imported {total_uploaded} new books to Supabase!", flush=True)
