import os
import re
import json
import time
import requests
import html
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple, Set
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
try:
    from fastembed import TextEmbedding
    _USE_FASTEMBED = True
except ImportError:
    from sentence_transformers import SentenceTransformer
    _USE_FASTEMBED = False

load_dotenv()

# Configurable hyperparameters (overridable via .env)
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.45"))
MIN_QUALITY_CANDIDATES = int(os.getenv("MIN_QUALITY_CANDIDATES", "6"))
GOOGLE_BOOKS_MAX_RESULTS = int(os.getenv("GOOGLE_BOOKS_MAX_RESULTS", "30"))
SIMILAR_THRESHOLD = float(os.getenv("SIMILAR_THRESHOLD", "0.55"))
SIMILAR_MIN_QUALITY = int(os.getenv("SIMILAR_MIN_QUALITY", "4"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# Path configuration
CHROMA_DIR = os.getenv("CHROMA_DB_PATH", os.path.join(os.path.dirname(__file__), "chroma_db"))
ZIP_PATH = os.path.join(os.path.dirname(__file__), "chroma_db.zip")
SQLITE_PATH = os.path.join(CHROMA_DIR, "chroma.sqlite3")

# Automatically extract database if chroma.sqlite3 is missing or is an empty initialization (<50MB)
if (not os.path.exists(SQLITE_PATH) or os.path.getsize(SQLITE_PATH) < 50_000_000) and os.path.exists(ZIP_PATH):
    import zipfile
    print(f"[Startup] Extracting library database from {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(__file__))
    print(f"[Startup] Database extraction complete! Database size: {os.path.getsize(SQLITE_PATH) if os.path.exists(SQLITE_PATH) else 0}")

COLLECTION_NAME = "bookmind_library"

# Initialize ChromaDB persistent client
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
books_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

def ensure_database_loaded():
    """Self-healing function to verify ChromaDB collection has books, extracting if needed."""
    global chroma_client, books_collection
    try:
        sqlite_size = os.path.getsize(SQLITE_PATH) if os.path.exists(SQLITE_PATH) else 0
        if sqlite_size < 50_000_000 and os.path.exists(ZIP_PATH):
            import zipfile
            print(f"[Self-Healing] Database is empty ({sqlite_size} bytes). Extracting {ZIP_PATH}...")
            with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(__file__))
            chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
            books_collection = chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[Self-Healing] Extraction complete! Collection count: {books_collection.count()}")
    except Exception as e:
        print(f"[Self-Healing Error]: {e}")
    return books_collection.count()

# In-memory Query Embedding Cache (maps query_text -> 384-dim list)
_QUERY_EMBEDDING_CACHE: Dict[str, List[float]] = {}
_QUERY_CACHE_MAX_SIZE = 1000

# In-memory Google Books API Response Cache (maps query_key -> (timestamp, List[items]))
_GOOGLE_BOOKS_QUERY_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}

# Initialize lightweight embedding model (384-dimensional dense embeddings)
_EMBEDDING_MODEL: Any = None

def get_embedding_model() -> Any:
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        if _USE_FASTEMBED:
            print("[Embedding Model] Loading ultra-low-memory FastEmbed ONNX model (all-MiniLM-L6-v2)...")
            _EMBEDDING_MODEL = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", threads=1)
        else:
            print("[Embedding Model] Loading SentenceTransformer embedding model (all-MiniLM-L6-v2)...")
            _EMBEDDING_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _EMBEDDING_MODEL


def get_or_create_query_embedding(query_text: str) -> List[float]:
    """Retrieve query embedding from cache or generate once using the unified embedding model."""
    clean_q = query_text.strip().lower()
    if not clean_q:
        clean_q = "popular acclaimed books"

    if clean_q in _QUERY_EMBEDDING_CACHE:
        return _QUERY_EMBEDDING_CACHE[clean_q]

    model = get_embedding_model()
    if _USE_FASTEMBED:
        vec = list(model.embed([clean_q]))[0].tolist()
    else:
        vec = model.encode([clean_q], normalize_embeddings=True)[0].tolist()

    if len(_QUERY_EMBEDDING_CACHE) >= _QUERY_CACHE_MAX_SIZE:
        # Evict oldest entries
        keys_to_remove = list(_QUERY_EMBEDDING_CACHE.keys())[:100]
        for k in keys_to_remove:
            _QUERY_EMBEDDING_CACHE.pop(k, None)

    _QUERY_EMBEDDING_CACHE[clean_q] = vec
    return vec


# ── GENRE TAXONOMY & RULES ──────────────────────────────────────────

GENRE_MAP: Dict[str, Dict[str, Any]] = {
    'Psychology': {
        'patterns': [r'\bpsycholog', r'\bcognitive\b', r'\bpsychiatr', r'\bpsychoanal', r'\bneuroscience\b', r'\bmental health\b', r'\bpsychotherap'],
        'google_query': 'subject:psychology'
    },
    'Philosophy': {
        'patterns': [r'\bphilosoph', r'\bethics\b', r'\bexistential', r'\bstoic', r'\blogic\b', r'\bmetaphysic'],
        'google_query': 'subject:philosophy'
    },
    'History': {
        'patterns': [r'\bhistory\b', r'\bhistorical\b', r'\bcivilization\b', r'\bworld war\b', r'\bmilitary history\b', r'\bmiddle ages\b', r'\bancient history\b', r'\bholocaust\b', r'\bpresidents\b'],
        'google_query': 'subject:history'
    },
    'Biography': {
        'patterns': [r'\bbiography\b', r'\bautobiography\b', r'\bmemoir', r'\bdiaries\b', r'\bpersonal narratives\b'],
        'google_query': 'subject:"biography & autobiography"'
    },
    'Self Development': {
        'patterns': [r'\bself-help\b', r'\bsuccess in business\b', r'\bpersonal finance\b', r'\bconduct of life\b', r'\btime management\b', r'\bleadership\b', r'\bfinance, personal\b', r'\bsuccess\b', r'\bmindset\b', r'\bhabits?\b'],
        'google_query': 'subject:"self-help"'
    },
    'Children\'s Fiction': {
        'patterns': [r'\bjuvenile fiction\b', r'\bchildren\'s stories\b', r'\bpicture books for children\b', r'\bfairy tales\b', r'\bchildren\'s poetry\b'],
        'google_query': 'subject:"juvenile fiction"'
    },
    'Children\'s Nonfiction': {
        'patterns': [r'\bjuvenile nonfiction\b', r'\bchildren\'s literature -- educational\b'],
        'google_query': 'subject:"juvenile nonfiction"'
    },
    'Science Fiction': {
        'patterns': [r'\bscience fiction\b', r'\bdystopias\b', r'\bcyberpunk\b', r'\btime travel\b', r'\bspace warfare\b', r'\binterplanetary\b', r'\balien\b', r'\brobots\b', r'\bspace opera\b'],
        'google_query': 'subject:"science fiction"'
    },
    'Fantasy': {
        'patterns': [r'\bfantasy fiction\b', r'\bfantasy\b', r'\bmagic\b', r'\bwizards\b', r'\bdragons\b', r'\bmythology\b', r'\bhigh fantasy\b'],
        'google_query': 'subject:fantasy'
    },
    'Mystery': {
        'patterns': [r'\bdetective and mystery\b', r'\bmystery\b', r'\bcrime\b', r'\bmurder\b', r'\bpolice procedural\b', r'\bprivate investigators\b', r'\bsherlock holmes\b'],
        'google_query': 'subject:mystery'
    },
    'Thriller': {
        'patterns': [r'\bthrillers?\b', r'\bsuspense\b', r'\bespionage\b', r'\bconspirac', r'\bspies\b', r'\bassassins\b', r'\bpsychological thriller\b'],
        'google_query': 'subject:thrillers'
    },
    'Horror': {
        'patterns': [r'\bhorror\b', r'\boccult\b', r'\bvampires\b', r'\bzombies\b', r'\bghosts\b', r'\bsupernatural\b', r'\bgothic fiction\b'],
        'google_query': 'subject:horror'
    },
    'Romance': {
        'patterns': [r'\bromance\b', r'\blove stories\b', r'\bromantic\b', r'\bcourtship\b', r'\bman-woman relationships\b'],
        'google_query': 'subject:romance'
    },
    'Young Adult': {
        'patterns': [r'\byoung adult\b', r'\bya fiction\b', r'\byoung adult fiction\b'],
        'google_query': 'subject:"young adult fiction"'
    },
    'Nonfiction': {
        'patterns': [r'\bnonfiction\b', r'\bscience\b', r'\bsocial science\b', r'\breligion\b', r'\bart\b', r'\bcooking\b', r'\bhealth & fitness\b', r'\bcomputers\b', r'\bmedical\b', r'\bnature\b', r'\beducation\b', r'\bmusic\b', r'\btravel\b'],
        'google_query': 'subject:nonfiction'
    },
    'Fiction': {
        'patterns': [r'\bfiction\b', r'\bdrama\b', r'\bpoetry\b', r'\bliterary collections\b', r'\bliterary criticism\b'],
        'google_query': 'subject:fiction'
    }
}

CANONICAL_AUTHORS: Dict[str, List[str]] = {
    'Mystery': ['agatha christie', 'arthur conan doyle', 'michael connelly', 'raymond chandler', 'john le carre', 'dorothy l. sayers', 'georges simenon', 'ian rankin', 'james patterson', 'lee child', 'edgar allan poe', 'ruth rendell', 'p.d. james', 'gillian flynn', 'dan brown'],
    'Science Fiction': ['isaac asimov', 'arthur c. clarke', 'philip k. dick', 'frank herbert', 'h.g. wells', 'robert a. heinlein', 'ray bradbury', 'william gibson', 'ursula k. le guin', 'neal stephenson', 'dan simmons', 'orson scott card', 'stanislaw lem', 'douglas adams', 'greg egan', 'iain m. banks', 'vernor vinge', 'cixin liu', 'andy weir'],
    'Fantasy': ['j.r.r. tolkien', 'george r.r. martin', 'brandon sanderson', 'terry pratchett', 'neil gaiman', 'patrick rothfuss', 'robert jordan', 'robin hobb', 'andrzej sapkowski', 'c.s. lewis', 'j.k. rowling', 'philip pullman', 'rick riordan', 'suzanne collins'],
    'Horror': ['stephen king', 'h.p. lovecraft', 'clive barker', 'dean koontz', 'bram stoker', 'mary shelley', 'shirley jackson', 'anne rice', 'peter straub', 'robert bloch', 'thomas harris'],
    'Romance': ['jane austen', 'nicholas sparks', 'danielle steel', 'nora roberts', 'emily bronte', 'charlotte bronte', 'julia quinn', 'colleen hoover', 'georgette heyer', 'stephenie meyer'],
    'Philosophy': ['plato', 'aristotle', 'marcus aurelius', 'friedrich nietzsche', 'jean-paul sartre', 'albert camus', 'immanuel kant', 'bertrand russell', 'arthur schopenhauer', 'rene descartes', 'baruch spinoza', 'john locke', 'david hume', 'hermann hesse', 'seneca'],
    'Psychology': ['sigmund freud', 'carl jung', 'daniel kahneman', 'oliver sacks', 'malcolm gladwell', 'b.f. skinner', 'jean piaget', 'viktor frankl', 'jordan peterson', 'steven pinker', 'mihaly csikszentmihalyi', 'robert cialdini', 'morgan housel', 'bessel van der kolk'],
    'Self Development': ['dale carnegie', 'stephen r. covey', 'napoleon hill', 'robert kiyosaki', 'james clear', 'tim ferriss', 'brian tracy', 'tony robbins', 'david goggins', 'cal newport', 'mark manson', 'simon sinek', 'robin sharma', 'spencer johnson'],
    'Biography': ['walter isaacson', 'ron chernow', 'david mccullough', 'robert caro', 'maya angelou', 'anne frank', 'doris kearns goodwin', 'barack obama', 'michelle obama']
}


def normalize_string(s: str) -> str:
    """Normalize text for consistent comparison."""
    if not s:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', s)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def make_dedup_key(title: str, author: str) -> str:
    """Generate a clean canonical slug for title + author deduplication."""
    # Strip subtitle after colon, dash, or parentheses to deduplicate multiple editions
    t_base = re.split(r'[:\-\(]', title or '')[0].strip()
    t_clean = re.sub(r'[^a-zA-Z0-9]', '', t_base.lower())
    # Author primary name
    a_base = (author or "").split(',')[0].split(' and ')[0].strip()
    a_clean = re.sub(r'[^a-zA-Z0-9]', '', a_base.lower())
    return f"{t_clean}_{a_clean[:12]}"


def classify_book_genres(raw_cat: str, authors: str, title: str, fallback_genre: Optional[str] = None) -> Tuple[str, List[str]]:
    """Determine the primary genre and all matching genres for a book."""
    raw_lower = str(raw_cat or '').lower()
    authors_lower = str(authors or '').lower()
    title_lower = str(title or '').lower()

    genres = set()

    # 1. Author check
    for g, auth_list in CANONICAL_AUTHORS.items():
        if any(auth in authors_lower for auth in auth_list):
            genres.add(g)

    # 2. Raw Category pattern check
    for g, conf in GENRE_MAP.items():
        if g in ['Fiction', 'Nonfiction']:
            continue
        for pat in conf['patterns']:
            if re.search(pat, raw_lower):
                genres.add(g)
                break

    # 3. If fallback genre explicitly requested
    if fallback_genre and fallback_genre in GENRE_MAP:
        genres.add(fallback_genre)

    # 4. Fallback broad category
    if not genres:
        if any(re.search(pat, raw_lower) for pat in GENRE_MAP['Nonfiction']['patterns']) or 'nonfiction' in raw_lower:
            genres.add('Nonfiction')
        else:
            genres.add('Fiction')

    # Primary genre selection
    specific_priority = [
        'Science Fiction', 'Fantasy', 'Horror', 'Mystery', 'Thriller', 'Romance',
        'Psychology', 'Philosophy', 'Biography', 'Self Development', 'History',
        'Young Adult', "Children's Fiction", "Children's Nonfiction"
    ]
    if fallback_genre and fallback_genre in genres:
        primary = fallback_genre
    else:
        primary = 'Fiction'
        for g in specific_priority:
            if g in genres:
                primary = g
                break
        if primary == 'Fiction' and 'Nonfiction' in genres:
            primary = 'Nonfiction'

    return primary, list(genres)


_COVER_CACHE: Dict[str, str] = {}


def resolve_authentic_cover(title: str, author: str, isbn_13: str = "", isbn_10: str = "", google_thumb: str = "") -> str:
    """Resolve the authentic real book cover photo from Google Content CDN or OpenLibrary."""
    clean_isbn = re.sub(r'[^0-9X]', '', str(isbn_13 or isbn_10 or '')).strip()
    if clean_isbn and len(clean_isbn) >= 9 and clean_isbn != "0":
        return f"https://books.google.com/books/content?vid=ISBN{clean_isbn}&printsec=frontcover&img=1&zoom=1"

    clean_t = re.split(r'[:\-\(]', title)[0].strip()
    clean_a = (author or "").split(',')[0].split(' and ')[0].strip()
    cache_key = f"{clean_t}_{clean_a}".lower().strip()
    if cache_key in _COVER_CACHE:
        return _COVER_CACHE[cache_key]

    # Try OpenLibrary search for high quality retail photo
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": clean_t, "limit": 4},
            headers={"User-Agent": "BookMind/2.0"},
            timeout=3.0
        )
        if resp.status_code == 200:
            docs = resp.json().get("docs", [])
            for d in docs:
                cid = d.get("cover_i")
                if cid:
                    real_cover = f"https://covers.openlibrary.org/b/id/{cid}-L.jpg"
                    _COVER_CACHE[cache_key] = real_cover
                    return real_cover
                isbns = d.get("isbn", [])
                if isbns:
                    clean_doc_isbn = re.sub(r'[^0-9X]', '', isbns[0]).strip()
                    if clean_doc_isbn:
                        real_cover = f"https://books.google.com/books/content?vid=ISBN{clean_doc_isbn}&printsec=frontcover&img=1&zoom=1"
                        _COVER_CACHE[cache_key] = real_cover
                        return real_cover
    except Exception:
        pass

    # If not found on OpenLibrary, use Google Thumb if valid
    if google_thumb and "placeholder" not in google_thumb and "cover-not-found" not in google_thumb:
        return google_thumb

    return ""



# ── FAMOUS AUTHORS & VIP BOOK EXCEPTION ───────────────────────────────
FAMOUS_AUTHORS: Set[str] = {
    # Classics & Literature
    "william shakespeare", "shakespeare", "jane austen", "george orwell", "charles dickens",
    "leo tolstoy", "tolstoy", "fyodor dostoevsky", "dostoevsky", "franz kafka", "kafka",
    "ernest hemingway", "hemingway", "f. scott fitzgerald", "fitzgerald", "mark twain",
    "oscar wilde", "virginia woolf", "homer", "dante alighieri", "victor hugo",
    "emily bronte", "charlotte bronte", "marcel proust", "gabriel garcia marquez",
    "j.r.r. tolkien", "tolkien", "c.s. lewis", "arthur conan doyle", "agatha christie",
    "edgar allan poe", "mary shelley", "roald dahl", "herman melville", "james joyce",
    "jules verne", "h.g. wells", "rabindranath tagore", "munshi premchand", "r.k. narayan",
    
    # Sci-Fi, Fantasy & Fiction
    "isaac asimov", "asimov", "arthur c. clarke", "philip k. dick", "frank herbert",
    "george r.r. martin", "j.k. rowling", "stephen king", "neil gaiman", "haruki murakami",
    "cormac mccarthy", "kurt vonnegut", "ray bradbury", "ursula k. le guin", "aldous huxley",
    "william gibson", "dan brown", "suzanne collins",
    
    # Philosophy, Science & Thought
    "plato", "aristotle", "socrates", "marcus aurelius", "seneca", "friedrich nietzsche",
    "nietzsche", "immanuel kant", "albert camus", "camus", "jean-paul sartre", "sartre",
    "rene descartes", "john locke", "arthur schopenhauer", "baruch spinoza", "sun tzu",
    "lao tzu", "confucius", "carl jung", "sigmund freud", "charles darwin", "albert einstein",
    "richard feynman", "carl sagan", "stephen hawking", "yuval noah harari", "daniel kahneman",
    "viktor frankl", "viktor e. frankl", "hermann hesse",
    
    # Self-Development & Modern Classics
    "james clear", "dale carnegie", "stephen r. covey", "robert greene", "morgan housel",
    "cal newport", "robert cialdini", "nassim nicholas taleb", "walter isaacson", "david goggins"
}


def is_bestseller_title(title: str) -> bool:
    """Return True if book title is a generic 'Bestseller' meta-guide or placeholder."""
    if not title:
        return True
    t_clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower()).strip()
    if t_clean in {"bestseller", "bestsellers", "the bestseller", "the bestsellers", "a bestseller", "best seller", "best sellers"}:
        return True
    if t_clean.startswith("bestseller ") or t_clean.startswith("bestsellers ") or t_clean.startswith("the bestseller ") or t_clean.startswith("the bestsellers "):
        return True
    if "bestseller popular fiction" in t_clean or "richard josephs bestseller" in t_clean or "richard joseph bestsellers" in t_clean or "richard josephs bestsellers" in t_clean:
        return True
    if "bestseller code" in t_clean or "how to write a bestseller" in t_clean or "art of writing blockbusters" in t_clean:
        return True
    return False


def is_famous_author(author_str: str) -> bool:
    if not author_str:
        return False
    a_low = author_str.lower()
    for famous in FAMOUS_AUTHORS:
        if famous in a_low:
            return True
    return False


def build_semantic_text(title: str, authors: str, primary_genre: str, categories: str, description: str) -> str:
    """Build high-quality rich text representation for semantic vector embedding."""
    desc_clean = normalize_string(description)
    trunc_desc = " ".join(desc_clean.split()[:120])
    return f"{title} by {authors}. Genre: {primary_genre}. Categories: {categories}. {trunc_desc}".strip()


# ── INGESTION PIPELINE ───────────────────────────────────────────────

class BookIngestionService:
    """Service to fetch, clean, deduplicate, embed, and store books in ChromaDB."""

    def __init__(self):
        self.collection = books_collection
        self.embedding_model = get_embedding_model()
        self.api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) BookMind/2.0'}

    def get_existing_ids_and_keys(self) -> Tuple[Set[str], Set[str]]:
        """Retrieve existing IDs, ISBNs, and deduplication keys from ChromaDB."""
        try:
            count = self.collection.count()
            if count == 0:
                return set(), set()
            
            res = self.collection.get(include=["metadatas"])
            existing_ids = set(res["ids"])
            existing_keys = set()
            for m in res.get("metadatas", []):
                if m:
                    key = m.get("dedup_key")
                    if key:
                        existing_keys.add(key)
                    isbn13 = m.get("isbn_13")
                    if isbn13:
                        existing_keys.add(str(isbn13).strip())
                    isbn10 = m.get("isbn_10")
                    if isbn10:
                        existing_keys.add(str(isbn10).strip())
                    gb_id = m.get("google_books_id")
                    if gb_id:
                        existing_keys.add(str(gb_id).strip())
                    title_author = make_dedup_key(m.get("title", ""), m.get("authors", ""))
                    if title_author:
                        existing_keys.add(title_author)
            return existing_ids, existing_keys
        except Exception as e:
            print(f"[Deduplication Warning] Error fetching existing ChromaDB keys: {e}")
            return set(), set()

    def fetch_from_google_books(
        self,
        query: str,
        max_results: int = GOOGLE_BOOKS_MAX_RESULTS,
        genre_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch volumes from Google Books API with caching and pagination protection."""
        q_str = query.strip()
        if genre_filter and genre_filter in GENRE_MAP:
            g_query = GENRE_MAP[genre_filter]['google_query']
            if q_str and q_str.lower() != 'popular' and q_str.lower() != genre_filter.lower():
                final_q = f"{q_str} {g_query}"
            else:
                final_q = g_query
        else:
            final_q = q_str if q_str else "bestseller"

        cache_key = f"{final_q.lower().strip()}_{max_results}"
        now = time.time()

        # Check API response cache
        if cache_key in _GOOGLE_BOOKS_QUERY_CACHE:
            cached_time, cached_items = _GOOGLE_BOOKS_QUERY_CACHE[cache_key]
            if now - cached_time < CACHE_TTL_SECONDS:
                print(f"[Google Books API Cache Hit] Reusing {len(cached_items)} candidates for query: '{final_q}'")
                return cached_items

        all_items = []
        start_index = 0
        batch_size = 20

        while len(all_items) < max_results:
            params = {
                "q": final_q,
                "startIndex": start_index,
                "maxResults": min(batch_size, max_results - len(all_items)),
                "printType": "books",
                "orderBy": "relevance",
                "langRestrict": "en"
            }
            if self.api_key:
                params["key"] = self.api_key

            try:
                resp = requests.get(
                    "https://www.googleapis.com/books/v1/volumes",
                    params=params,
                    headers=self.headers,
                    timeout=8.0
                )
                if resp.status_code != 200:
                    print(f"[Google Books API] Response status {resp.status_code} for query '{final_q}'")
                    break

                data = resp.json()
                items = data.get("items", [])
                if not items:
                    break

                all_items.extend(items)
                start_index += len(items)
                if len(items) < batch_size:
                    break
                time.sleep(0.08)  # Rate limiting protection
            except Exception as e:
                print(f"[Google Books API Error] Failed fetching volumes: {e}")
                break

        # Cache results (even if empty to prevent repeated hammering)
        _GOOGLE_BOOKS_QUERY_CACHE[cache_key] = (now, all_items)
        return all_items

    def fetch_from_open_library(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch books directly from OpenLibrary Search API."""
        try:
            resp = requests.get(
                "https://openlibrary.org/search.json",
                params={"q": query, "limit": limit},
                headers={"User-Agent": "BookMindApp/2.0 (https://bookmind.app)"},
                timeout=6.0
            )
            if resp.status_code != 200:
                return []
            docs = resp.json().get("docs", [])
            records = []
            for doc in docs:
                title = normalize_string(doc.get("title", ""))
                if not title or len(title) < 2:
                    continue
                author_names = doc.get("author_name", [])
                authors_str = ", ".join(author_names[:2]) if author_names else "Unknown Author"
                
                # ISBN and Covers
                isbn_list = doc.get("isbn", [])
                clean_isbn_13 = ""
                clean_isbn_10 = ""
                for raw_isbn in isbn_list:
                    c = re.sub(r'[^0-9X]', '', str(raw_isbn)).strip()
                    if len(c) == 13 and not clean_isbn_13:
                        clean_isbn_13 = c
                    elif len(c) == 10 and not clean_isbn_10:
                        clean_isbn_10 = c
                
                cover_id = doc.get("cover_i")
                if cover_id:
                    thumb = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                elif clean_isbn_13:
                    thumb = f"https://covers.openlibrary.org/b/isbn/{clean_isbn_13}-L.jpg"
                elif clean_isbn_10:
                    thumb = f"https://covers.openlibrary.org/b/isbn/{clean_isbn_10}-L.jpg"
                else:
                    thumb = ""
                
                subjects = doc.get("subject", [])
                raw_cat_str = ", ".join(subjects[:5]) if subjects else "General Literature"
                
                primary_genre, genres_list = classify_book_genres(raw_cat_str, title, raw_cat_str)
                
                first_sentence = doc.get("first_sentence", "")
                if isinstance(first_sentence, dict):
                    first_sentence = first_sentence.get("value", "")
                elif isinstance(first_sentence, list):
                    first_sentence = " ".join(first_sentence)
                
                desc = first_sentence or f"A celebrated work by {authors_str} exploring {primary_genre}."
                
                ol_key = doc.get("key", "").replace("/", "_")
                doc_id = f"ol_{ol_key}" if ol_key else f"isbn_{clean_isbn_13 or clean_isbn_10 or make_dedup_key(title, authors_str)}"
                
                semantic_doc = build_semantic_text(title, authors_str, primary_genre, raw_cat_str, desc)
                
                records.append({
                    "id": doc_id,
                    "google_books_id": "",
                    "title": title,
                    "authors": authors_str,
                    "description": desc[:240],
                    "full_description": desc,
                    "categories": raw_cat_str,
                    "genre": primary_genre,
                    "genres_json": json.dumps(genres_list),
                    "publisher": doc.get("publisher", [""])[0] if doc.get("publisher") else "",
                    "published_date": str(doc.get("first_publish_year", "")),
                    "isbn_10": clean_isbn_10,
                    "isbn_13": clean_isbn_13,
                    "page_count": doc.get("number_of_pages_median") or 0,
                    "language": doc.get("language", ["en"])[0] if doc.get("language") else "en",
                    "thumbnail": thumb,
                    "preview_link": "",
                    "info_link": f"https://openlibrary.org{doc.get('key', '')}",
                    "source": "OpenLibrary",
                    "rating": 4.8 if is_famous_author(authors_str) else 4.5,
                    "dedup_key": make_dedup_key(title, authors_str),
                    "created_at": int(time.time()),
                    "semantic_doc": semantic_doc
                })
            return records
        except Exception as e:
            print(f"[OpenLibrary API Error]: {e}")
            return []

    def clean_and_normalize_volume(
        self,
        item: Dict[str, Any],
        fallback_genre: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Validate, clean, normalize metadata, and check quality of a Google Books item."""
        vol = item.get("volumeInfo", {})
        gb_id = item.get("id") or ""
        title = normalize_string(vol.get("title", ""))

        # 1. Quality & Spam Filters
        t_low = title.lower()
        if not title or t_low == "unknown title" or len(title) < 2:
            return None
        
        # Authors
        authors_list = vol.get("authors", [])
        if not authors_list:
            authors_str = "Unknown Author"
        elif len(authors_list) == 2:
            authors_str = f"{normalize_string(authors_list[0])} and {normalize_string(authors_list[1])}"
        elif len(authors_list) > 2:
            authors_str = f"{', '.join(normalize_string(a) for a in authors_list[:-1])}, and {normalize_string(authors_list[-1])}"
        else:
            authors_str = normalize_string(authors_list[0])

        # Reject poor-quality records with unknown author and no identifier
        industry_ids = vol.get("industryIdentifiers", [])
        if authors_str == "Unknown Author" and not industry_ids:
            return None
        
        # Filter spam summaries, workbooks, notes, market catalogues and third-party analysis
        spam_patterns = [
            r'\bsummary\b', r'\banalysis of\b', r'\bworkbook\b', r'\bguidebook\b',
            r'\bstudy guide\b', r'\bcompanion to\b', r'\bkey takeaways\b',
            r'\bnotes on\b', r'\bjournal\b', r'\bnotebook\b', r'\bcalendar\b',
            r'\bplanner\b', r'\bcondensed version\b', r'\bunauthorized\b',
            r'\baction guide\b', r'\bquick read\b', r'\bcheat sheet\b',
            r'\bcatalogue of\b', r'\bwriter\'s market\b', r'\bwriters market\b',
            r'\breview of contemporary\b', r'\bliterature in the marketplace\b',
            r'\bby achievement pyramid\b', r'\bby quality summaries\b',
            r'\bby black book\b', r'\bby easyprint\b'
        ]
        if any(re.search(pat, t_low) for pat in spam_patterns):
            return None

        # Filter translation subtitle tags
        if re.search(r'\((tamil|hindi|marathi|kannada|telugu|gujarati|bengali|spanish|french|german|russian|chinese|japanese|korean)\b', t_low):
            return None

        # Reject generic bestseller meta-titles / publishing guides
        if is_bestseller_title(title):
            return None

        # Description
        raw_desc = vol.get("description", "")
        clean_desc = normalize_string(raw_desc)
        desc_words = clean_desc.split()
        trunc_desc = " ".join(desc_words[:35]) + ("..." if len(desc_words) > 35 else "")

        # Categories
        categories_list = vol.get("categories", [])
        raw_cat_str = ", ".join(categories_list)

        # Classify genre
        primary_genre, genres_list = classify_book_genres(raw_cat_str, authors_str, title, fallback_genre)

        # ISBNs
        industry_ids = vol.get("industryIdentifiers", [])
        isbn_10 = ""
        isbn_13 = ""
        for iid in industry_ids:
            itype = iid.get("type", "")
            ident = iid.get("identifier", "")
            if itype == "ISBN_13":
                isbn_13 = ident
            elif itype == "ISBN_10":
                isbn_10 = ident

        # Thumbnail resolution: Google Books HD or OpenLibrary Real Retail Cover
        img_links = vol.get("imageLinks", {})
        google_thumb = (
            img_links.get("extraLarge") or
            img_links.get("large") or
            img_links.get("medium") or
            img_links.get("thumbnail") or
            img_links.get("smallThumbnail") or
            ""
        )
        if google_thumb:
            if google_thumb.startswith("http://"):
                google_thumb = google_thumb.replace("http://", "https://")
            google_thumb = re.sub(r'zoom=\d', 'zoom=1', google_thumb)
            google_thumb = google_thumb.replace('&edge=curl', '')

        thumb = resolve_authentic_cover(
            title=title,
            author=authors_str,
            isbn_13=isbn_13,
            isbn_10=isbn_10,
            google_thumb=google_thumb
        )

        # Rating resolution: Use official Google Books rating if present, or compute realistic rating
        avg_rating = vol.get("averageRating")
        if avg_rating is not None:
            try:
                rating_num = round(float(avg_rating), 1)
            except Exception:
                rating_num = 4.5
        else:
            if is_famous_author(authors_str):
                rating_num = 4.8
            else:
                # Deterministic natural rating between 4.1 and 4.8
                h = sum(ord(c) for c in (title + authors_str))
                rating_num = round(4.1 + ((h % 8) * 0.1), 1)

        # COVER POLICY: Strictly require a valid HTTP cover image - no exceptions
        if not thumb or not thumb.startswith("http") or "placeholder" in thumb or "cover-not-found" in thumb:
            return None

        doc_id = f"gb_{gb_id}" if gb_id else f"isbn_{isbn_13 or isbn_10 or make_dedup_key(title, authors_str)}"
        dedup_key = make_dedup_key(title, authors_str)

        semantic_doc = build_semantic_text(title, authors_str, primary_genre, raw_cat_str, clean_desc)

        return {
            "id": doc_id,
            "google_books_id": gb_id,
            "title": title,
            "authors": authors_str,
            "description": trunc_desc,
            "full_description": clean_desc,
            "categories": raw_cat_str,
            "genre": primary_genre,
            "genres_json": json.dumps(genres_list),
            "publisher": normalize_string(vol.get("publisher", "")),
            "published_date": str(vol.get("publishedDate", "")),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13,
            "page_count": int(vol.get("pageCount", 0)) if vol.get("pageCount") else 0,
            "language": vol.get("language", "en"),
            "thumbnail": thumb,
            "preview_link": vol.get("previewLink", ""),
            "info_link": vol.get("infoLink", ""),
            "source": "Google Books",
            "rating": rating_num,
            "dedup_key": dedup_key,
            "semantic_doc": semantic_doc,
            "created_at": int(time.time())
        }

    def ingest_books(
        self,
        query: str,
        count: int = GOOGLE_BOOKS_MAX_RESULTS,
        genre_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ingestion pipeline: Fetch -> Clean -> Deduplicate -> Embed ONLY new books -> Store in ChromaDB."""
        clean_q = query.strip()
        print(f"[Ingestion Pipeline] Starting dynamic ingestion: query='{clean_q}', max_count={count}, genre='{genre_filter}'...")
        
        # 1. Fetch raw items from Google Books
        raw_items = self.fetch_from_google_books(clean_q, max_results=count, genre_filter=genre_filter)
        
        # If specific book title query with few items, also fetch related domain candidates to enrich recommendations
        if len(raw_items) < 20 and not genre_filter and len(clean_q.split()) <= 4:
            subject_query = f"{clean_q} classic popular"
        print(f"[Ingestion Pipeline] Searching online for '{clean_q}' across Google Books and OpenLibrary...")

        existing_ids, existing_keys = self.get_existing_ids_and_keys()

        # Fetch from both Google Books and OpenLibrary
        gb_items = self.fetch_from_google_books(clean_q, max_results=GOOGLE_BOOKS_MAX_RESULTS, genre_filter=genre_filter)
        ol_records = self.fetch_from_open_library(clean_q, limit=15)

        valid_records = []
        dup_count = 0

        # Process Google Books candidates
        for item in gb_items:
            rec = self.clean_and_normalize_volume(item, fallback_genre=genre_filter)
            if not rec:
                continue
            if rec["id"] in existing_ids or (rec["google_books_id"] and rec["google_books_id"] in existing_keys):
                dup_count += 1
                continue
            if rec["dedup_key"] in existing_keys or (rec["isbn_13"] and rec["isbn_13"] in existing_keys):
                dup_count += 1
                continue
            if rec["isbn_10"] and rec["isbn_10"] in existing_keys:
                dup_count += 1
                continue

            existing_ids.add(rec["id"])
            existing_keys.add(rec["dedup_key"])
            valid_records.append(rec)
            if len(valid_records) >= count:
                break

        # Process OpenLibrary candidates
        for rec in ol_records:
            if len(valid_records) >= count:
                break
            if rec["id"] in existing_ids or rec["dedup_key"] in existing_keys:
                dup_count += 1
                continue
            if rec["isbn_13"] and rec["isbn_13"] in existing_keys:
                dup_count += 1
                continue
            if rec["isbn_10"] and rec["isbn_10"] in existing_keys:
                dup_count += 1
                continue

            existing_ids.add(rec["id"])
            existing_keys.add(rec["dedup_key"])
            valid_records.append(rec)

        print(f"[Online Search] Found {len(valid_records)} new books online for '{clean_q}' ({dup_count} duplicates skipped).")

        if not valid_records:
            return {"status": "success", "imported": 0, "duplicates": dup_count, "total_books": self.collection.count()}

        # Generate embeddings with FastEmbed or SentenceTransformers
        semantic_texts = [r["semantic_doc"] for r in valid_records]
        if _USE_FASTEMBED:
            embeddings = [list(e) for e in self.embedding_model.embed(semantic_texts, batch_size=1)]
        else:
            embeddings = self.embedding_model.encode(semantic_texts, show_progress_bar=False, normalize_embeddings=True)

        # Insert into ChromaDB
        ids = [r["id"] for r in valid_records]
        documents = semantic_texts
        metadatas = []
        for r in valid_records:
            meta = {
                "id": r["id"],
                "google_books_id": r["google_books_id"],
                "title": r["title"],
                "authors": r["authors"],
                "description": r["description"],
                "full_description": r["full_description"][:1000],
                "categories": r["categories"],
                "genre": r["genre"],
                "genres_json": r["genres_json"],
                "publisher": r["publisher"],
                "published_date": r["published_date"],
                "isbn_10": r["isbn_10"],
                "isbn_13": r["isbn_13"],
                "page_count": r["page_count"],
                "language": r["language"],
                "thumbnail": r["thumbnail"],
                "preview_link": r["preview_link"],
                "info_link": r["info_link"],
                "source": r["source"],
                "rating": r["rating"],
                "dedup_key": r["dedup_key"],
                "created_at": r["created_at"]
            }
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings,
            metadatas=metadatas,
            documents=documents
        )

        total_count = self.collection.count()
        print(f"[Storage] Stored {len(valid_records)} new books into ChromaDB (New total collection size: {total_count}).")
        return {
            "status": "success",
            "imported": len(valid_records),
            "duplicates": dup_count,
            "total_books": total_count,
            "sample_imported": [r["title"] for r in valid_records[:5]]
        }


# Singleton instance
ingestion_service = BookIngestionService()
