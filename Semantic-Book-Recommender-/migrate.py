import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("Loading books...")
books = pd.read_csv("books_with_emotions.csv")
books["large_thumbnail"] = books["thumbnail"] + "&fife=w800"
books["large_thumbnail"] = np.where(
    books["large_thumbnail"].isna(),
    "cover-not-found.jpg",
    books["large_thumbnail"],
)

print("Generating embeddings... (this may take a few minutes)")
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

descriptions = books["description"].fillna("").tolist()
embeddings = embeddings_model.embed_documents(descriptions)

print("Uploading to Supabase...")
batch_size = 50

for i in range(0, len(books), batch_size):
    batch = books.iloc[i:i+batch_size]
    batch_embeddings = embeddings[i:i+batch_size]

    records = []
    for j, (_, row) in enumerate(batch.iterrows()):
        records.append({
            "isbn13": int(row["isbn13"]) if not pd.isna(row["isbn13"]) else None,
            "title": str(row["title"]) if not pd.isna(row["title"]) else "",
            "authors": str(row["authors"]) if not pd.isna(row["authors"]) else "",
            "description": str(row["description"]) if not pd.isna(row["description"]) else "",
            "thumbnail": str(row["large_thumbnail"]) if not pd.isna(row["large_thumbnail"]) else "",
            "simple_categories": str(row["simple_categories"]) if not pd.isna(row["simple_categories"]) else "",
            "joy": float(row["joy"]) if not pd.isna(row["joy"]) else 0.0,
            "surprise": float(row["surprise"]) if not pd.isna(row["surprise"]) else 0.0,
            "anger": float(row["anger"]) if not pd.isna(row["anger"]) else 0.0,
            "fear": float(row["fear"]) if not pd.isna(row["fear"]) else 0.0,
            "sadness": float(row["sadness"]) if not pd.isna(row["sadness"]) else 0.0,
            "embedding": batch_embeddings[j],
        })

    supabase.table("books").insert(records).execute()
    print(f"Uploaded {min(i+batch_size, len(books))}/{len(books)} books...")

print("Migration complete! ✅")
