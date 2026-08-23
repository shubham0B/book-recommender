'use client'

import { useMemo, useState, useEffect, useRef } from 'react'
import { ArrowRight, BookOpen, Heart, Menu, Search, Sparkles, Star, UserRound, X, BookText, SlidersHorizontal, Check, ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { BookCoverImage } from '@/components/ui/book-cover-image'

const ALL_GENRES = [
  'Fiction',
  'Nonfiction',
  "Children's Fiction",
  "Children's Nonfiction",
  'Fantasy',
  'Science Fiction',
  'Mystery',
  'Thriller',
  'Horror',
  'Romance',
  'Self Development',
  'Psychology',
  'History',
  'Philosophy',
  'Biography',
  'Young Adult'
]

const books = [
  { title: 'The Hobbit', author: 'J.R.R. Tolkien', genre: 'Fantasy', rating: 4.8, isbn: '9780547928227', description: 'A reluctant hobbit leaves his quiet home for an unexpected journey through a world of dwarves, dragons, and ancient treasure.', thumbnail: 'https://m.media-amazon.com/images/I/710+5Jn83EL._AC_UF1000,1000_QL80_.jpg' },
  { title: "Harry Potter and the Sorcerer's Stone", author: 'J.K. Rowling', genre: 'Fantasy', rating: 4.9, isbn: '9780590353427', description: 'An ordinary boy discovers a hidden world of magic, friendship, and a destiny far greater than he imagined.', thumbnail: 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1474154022i/3.jpg' },
  { title: 'The Hunger Games', author: 'Suzanne Collins', genre: 'Fiction', rating: 4.8, isbn: '9780439023481', description: 'In the ruins of a place once known as North America lies the nation of Panem, a shining Capitol surrounded by twelve outlying districts.', thumbnail: 'https://m.media-amazon.com/images/I/61I24wOsn8L._AC_UF1000,1000_QL80_.jpg' },
  { title: '1984', author: 'George Orwell', genre: 'Fiction', rating: 4.7, isbn: '9780451524935', description: 'A haunting vision of a totalitarian future where truth, freedom, and even thought are under surveillance.', thumbnail: 'https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'To Kill a Mockingbird', author: 'Harper Lee', genre: 'Fiction', rating: 4.8, isbn: '9780061120084', description: 'A moving story of childhood, compassion, and moral courage in a deeply divided American town.', thumbnail: 'https://m.media-amazon.com/images/I/81aY1lxnorL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Dune', author: 'Frank Herbert', genre: 'Science Fiction', rating: 4.8, isbn: '9780441172719', description: 'Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world.', thumbnail: 'https://m.media-amazon.com/images/I/81ym3QUd3tL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'The Psychology of Money', author: 'Morgan Housel', genre: 'Self Development', rating: 4.7, isbn: '9780857197689', description: 'Timeless lessons on wealth, greed, and happiness told through insightful stories about how people think about money.', thumbnail: 'https://m.media-amazon.com/images/I/71g2ednj0JL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Atomic Habits', author: 'James Clear', genre: 'Self Development', rating: 4.8, isbn: '9780735211292', description: 'An easy and proven way to build good habits and break bad ones with actionable life strategies.', thumbnail: 'https://m.media-amazon.com/images/I/81F90H7hnML._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Sapiens: A Brief History of Humankind', author: 'Yuval Noah Harari', genre: 'History', rating: 4.6, isbn: '9780062316097', description: 'A sweeping exploration of how humankind came to dominate the planet and shape the modern world.', thumbnail: 'https://m.media-amazon.com/images/I/713jIoMO3UL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Pride and Prejudice', author: 'Jane Austen', genre: 'Romance', rating: 4.7, isbn: '9780141439518', description: 'A sparkling comedy of manners about first impressions, family expectations, and unexpected love.', thumbnail: 'https://m.media-amazon.com/images/I/81NLDvyAHrL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'The Shining', author: 'Stephen King', genre: 'Horror', rating: 4.6, isbn: '9780307743657', description: 'Jack Torrance takes a job as the winter caretaker at the Overlook Hotel, an isolated hotel with a dark history.', thumbnail: 'https://m.media-amazon.com/images/I/81U2fU1hUGL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'The Da Vinci Code', author: 'Dan Brown', genre: 'Mystery', rating: 4.5, isbn: '9780307474278', description: 'A murder in the Louvre leads symbologist Robert Langdon on a perilous quest through Paris and history.', thumbnail: 'https://m.media-amazon.com/images/I/815WUkQ1yvL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Thinking, Fast and Slow', author: 'Daniel Kahneman', genre: 'Psychology', rating: 4.6, isbn: '9780374533557', description: 'An exploration of the two systems that drive the way we think: fast, intuitive, and slow, deliberate.', thumbnail: 'https://m.media-amazon.com/images/I/71f6v0mmsxL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Meditations', author: 'Marcus Aurelius', genre: 'Philosophy', rating: 4.7, isbn: '9780812968255', description: 'Personal writings of the Roman Emperor on Stoic philosophy, duty, resilience, and wisdom.', thumbnail: 'https://m.media-amazon.com/images/I/81w+v2c06uL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Steve Jobs', author: 'Walter Isaacson', genre: 'Biography', rating: 4.7, isbn: '9781451648539', description: 'The riveting biography of the creative entrepreneur whose passion for perfection revolutionized six industries.', thumbnail: 'https://m.media-amazon.com/images/I/81VStYnDGrL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'The Fault in Our Stars', author: 'John Green', genre: 'Young Adult', rating: 4.4, isbn: '9780525478812', description: 'Despite the tumor-shrinking medical miracle that has bought her a few years, Hazel has never been anything but terminal.', thumbnail: 'https://m.media-amazon.com/images/I/81yAo5ElQlL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Matilda', author: 'Roald Dahl', genre: "Children's Fiction", rating: 4.7, isbn: '9780142410370', description: 'Matilda is a little girl with astonishing wit, intelligence, and psychokinetic powers who is unloved by her parents.', thumbnail: 'https://m.media-amazon.com/images/I/81xU9d6bXcL._AC_UF1000,1000_QL80_.jpg' },
  { title: "Charlotte's Web", author: 'E.B. White', genre: "Children's Fiction", rating: 4.8, isbn: '9780064400558', description: 'The tender story of a friendship between a pig named Wilbur and an extraordinary barn spider named Charlotte.', thumbnail: 'https://m.media-amazon.com/images/I/91Izs0JgLpL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'National Geographic Little Kids Big Book', author: 'Catherine D. Hughes', genre: "Children's Nonfiction", rating: 4.9, isbn: '9781426302916', description: 'Bursting with lively facts and colorful photos for curious young readers exploring animals and nature.', thumbnail: 'https://m.media-amazon.com/images/I/91b5+b0mGXL._AC_UF1000,1000_QL80_.jpg' },
  { title: 'Little People, BIG DREAMS: Maya Angelou', author: 'Lisbeth Kaiser', genre: "Children's Nonfiction", rating: 4.8, isbn: '9781847808905', description: 'Discover the life of Maya Angelou, the inspiring author, activist, and poet in this empowering story.', thumbnail: 'https://m.media-amazon.com/images/I/81iKqJjCsmL._AC_UF1000,1000_QL80_.jpg' }
]

type Book = (typeof books)[number] & {
  source?: string;
  links?: { info?: string; preview?: string };
}
function getFallbackCover(title: string = 'Book Title', author: string = 'Author', genre: string = 'Fiction'): string {
  const cleanTitle = (title || 'Untitled Book').replace(/[\r\n\t]+/g, ' ').trim();
  const cleanAuthor = (author || 'Unknown Author').replace(/[\r\n\t]+/g, ' ').trim();
  const cleanGenre = (genre || 'LITERATURE').toUpperCase();

  const gradients: Record<string, [string, string, string]> = {
    'Science Fiction': ['#020617', '#0f172a', '#1e3a8a'],
    'Fantasy': ['#1e1035', '#3b0764', '#581c87'],
    'Mystery': ['#0b0f19', '#1e1b4b', '#312e81'],
    'Thriller': ['#1c0404', '#450a0a', '#7f1d1d'],
    'Horror': ['#09090b', '#18181b', '#27272a'],
    'Romance': ['#2a0418', '#500724', '#831843'],
    'Self Development': ['#022c22', '#064e3b', '#047857'],
    'Psychology': ['#042f2e', '#134e4a', '#0f766e'],
    'Philosophy': ['#261502', '#451a03', '#78350f'],
    'History': ['#1c1917', '#292524', '#44403c'],
    'Biography': ['#0f172a', '#1e293b', '#334155'],
    'Fiction': ['#081b33', '#172554', '#1e3a8a'],
    'Nonfiction': ['#09131f', '#0f172a', '#1e293b'],
    'Young Adult': ['#2e022f', '#4a044e', '#701a75'],
    "Children's Fiction": ['#0f2e29', '#115e59', '#0d9488'],
  };

  const [bgDark, color1, color2] = gradients[genre] || ['#0f172a', '#1e293b', '#334155'];

  const words = cleanTitle.split(' ');
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    if ((currentLine + ' ' + word).trim().length <= 18) {
      currentLine = (currentLine + ' ' + word).trim();
    } else {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
      if (lines.length >= 4) break;
    }
  }
  if (currentLine && lines.length < 4) {
    lines.push(currentLine);
  }

  const fontSize = lines.length >= 4 ? 20 : lines.length === 3 ? 23 : 27;
  const lineHeight = fontSize * 1.35;
  const totalHeight = lines.length * lineHeight;
  const startY = 285 - (totalHeight / 2);

  const escapeXml = (unsafe: string) => unsafe.replace(/[<>&'"]/g, (c) => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
      default: return c;
    }
  });

  const titleSvgLines = lines
    .map((line, idx) => `<text x="200" y="${startY + (idx * lineHeight)}" text-anchor="middle" fill="#ffffff" font-family="'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif" font-size="${fontSize}" font-weight="700" letter-spacing="0.5" filter="url(#shadow)">${escapeXml(line)}</text>`)
    .join('\n');

  const authorY = Math.min(485, startY + totalHeight + 70);

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${bgDark}" />
        <stop offset="45%" stop-color="${color1}" />
        <stop offset="100%" stop-color="${color2}" />
      </linearGradient>
      <linearGradient id="spine" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#000" stop-opacity="0.6"/>
        <stop offset="15%" stop-color="#fff" stop-opacity="0.12"/>
        <stop offset="25%" stop-color="#000" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#000" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fbbf24" />
        <stop offset="50%" stop-color="#f59e0b" />
        <stop offset="100%" stop-color="#d97706" />
      </linearGradient>
      <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
        <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.7"/>
      </filter>
    </defs>

    <!-- Book Background -->
    <rect width="400" height="600" fill="url(#bg)" rx="10" />

    <!-- Left Spine Depth -->
    <rect width="46" height="600" fill="url(#spine)" />

    <!-- Ornate Double Gold Borders -->
    <rect x="22" y="22" width="356" height="556" fill="none" stroke="url(#gold)" stroke-width="1.8" stroke-opacity="0.7" rx="6" />
    <rect x="28" y="28" width="344" height="544" fill="none" stroke="url(#gold)" stroke-width="0.8" stroke-opacity="0.4" rx="4" />

    <!-- Corner Accents -->
    <text x="36" y="46" fill="#fbbf24" font-size="12" opacity="0.8">✦</text>
    <text x="364" y="46" fill="#fbbf24" font-size="12" opacity="0.8" text-anchor="end">✦</text>
    <text x="36" y="562" fill="#fbbf24" font-size="12" opacity="0.8">✦</text>
    <text x="364" y="562" fill="#fbbf24" font-size="12" opacity="0.8" text-anchor="end">✦</text>

    <!-- Genre Category Badge -->
    <rect x="120" y="55" width="160" height="24" rx="12" fill="#000" fill-opacity="0.4" stroke="url(#gold)" stroke-width="1" stroke-opacity="0.6"/>
    <text x="200" y="71" fill="#fbbf24" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="700" letter-spacing="2.5" text-anchor="middle">${escapeXml(cleanGenre)}</text>

    <!-- Book Title (Auto-Wrapped & Centered) -->
    ${titleSvgLines}

    <!-- Decorative Gold Divider -->
    <g transform="translate(140, ${startY + totalHeight + 18})">
      <line x1="0" y1="0" x2="45" y2="0" stroke="url(#gold)" stroke-width="1.5" stroke-opacity="0.7"/>
      <text x="60" y="4" fill="#fbbf24" font-size="10" text-anchor="middle">✦</text>
      <line x1="75" y1="0" x2="120" y2="0" stroke="url(#gold)" stroke-width="1.5" stroke-opacity="0.7"/>
    </g>

    <!-- Author Name -->
    <text x="200" y="${authorY}" text-anchor="middle" fill="#e2e8f0" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="600" letter-spacing="1.5" filter="url(#shadow)">
      ${escapeXml(cleanAuthor.toUpperCase())}
    </text>

    <!-- Footer Edition Ribbon -->
    <text x="200" y="540" text-anchor="middle" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="500" letter-spacing="2" opacity="0.85">
      ★ BOOKMIND LIBRARY EDITION ★
    </text>
  </svg>`;

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

const isBestsellerTitle = (title?: string): boolean => {
  if (!title) return true;
  const clean = title.toLowerCase().replace(/[^a-z0-9\s]/g, '').trim();
  if (['bestseller', 'bestsellers', 'the bestseller', 'the bestsellers', 'a bestseller', 'best seller', 'best sellers'].includes(clean)) return true;
  if (clean.startsWith('bestseller ') || clean.startsWith('bestsellers ') || clean.startsWith('the bestseller ')) return true;
  if (clean.includes('bestseller popular fiction') || clean.includes('richard joseph') || clean.includes('bestseller code')) return true;
  return false;
};

const isValidCover = (thumb?: string, isbn?: string): boolean => {
  if (thumb && typeof thumb === 'string') {
    const t = thumb.trim();
    if (t.startsWith('http') && !t.includes('placeholder') && !t.includes('cover-not-found') && !t.startsWith('data:image/svg')) {
      return true;
    }
  }
  const cleanIsbn = (isbn || '').replace(/[^0-9X]/gi, '').trim();
  if (cleanIsbn.length >= 9 && cleanIsbn !== '0') {
    return true;
  }
  return false;
};

function isMatchingGenre(bookGenre?: string, targetGenres?: string[]): boolean {
  if (!targetGenres || targetGenres.length === 0 || targetGenres.includes('All')) return true;
  if (!bookGenre) return false;
  const bg = bookGenre.toLowerCase().trim();
  return targetGenres.some(tg => {
    const target = tg.toLowerCase().trim();
    if (bg === target) return true;
    if (target === 'fiction' && bg.includes('fiction') && !bg.includes('nonfiction')) return true;
    if (target === 'nonfiction' && bg.includes('nonfiction')) return true;
    if (target === 'science fiction' && (bg.includes('sci-fi') || bg.includes('science fiction'))) return true;
    if (target === "children's fiction" && bg.includes("children") && bg.includes("fiction") && !bg.includes("nonfiction")) return true;
    if (target === "children's nonfiction" && bg.includes("children") && bg.includes("nonfiction")) return true;
    return bg.includes(target) || target.includes(bg);
  });
}

const cover = (isbn?: string, thumbnail?: string, title?: string, author?: string, genre?: string) => {
  if (isValidCover(thumbnail, isbn)) {
    return thumbnail!;
  }
  const cleanIsbn = (isbn || '').replace(/[^0-9X]/gi, '').trim();
  if (cleanIsbn.length >= 9 && cleanIsbn !== '0') {
    return `https://books.google.com/books/content?vid=ISBN${cleanIsbn}&printsec=frontcover&img=1&zoom=1`;
  }
  return '';
}
const filters = [
  'All',
  'Fiction',
  'Nonfiction',
  'Fantasy',
  'Science Fiction',
  'Mystery',
  'Thriller',
  'Horror',
  'Romance',
  'Self Development',
  'Psychology',
  'History',
  'Philosophy',
  'Biography',
  'Young Adult',
  "Children's Fiction",
  "Children's Nonfiction"
]

interface SuggestionItem {
  title: string;
  author: string;
  genre: string;
  thumbnail: string;
  isbn?: string;
}

function HighlightMatch({ text, highlight }: { text: string; highlight: string }) {
  if (!highlight.trim()) return <span>{text}</span>;
  const escaped = highlight.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const parts = text.split(new RegExp(`(${escaped})`, 'gi'));
  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === highlight.toLowerCase().trim() ? (
          <span key={i} className="font-semibold text-primary underline decoration-primary/50 decoration-2 underline-offset-2">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}

function BookCard({ 
  book, 
  onSelect,
  isLiked,
  onToggleLike,
  onCoverFailed
}: { 
  book: Book; 
  onSelect: (book: Book) => void;
  isLiked?: boolean;
  onToggleLike?: (book: Book) => void;
  onCoverFailed?: (bookKey: string) => void;
}) {
  const isExternal = book.source === 'Google Books'
  const displayRating = typeof book.rating === 'number' ? book.rating.toFixed(1) : (Number(book.rating) || 4.5).toFixed(1)

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl relative">
      {/* Top Left: Like / Favorite Button */}
      {onToggleLike && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onToggleLike(book);
          }}
          aria-label={isLiked ? `Unlike ${book.title}` : `Like ${book.title}`}
          title={isLiked ? "Saved in Liked Books" : "Add to Liked Books"}
          className={`absolute top-2.5 left-2.5 z-20 flex size-9 items-center justify-center rounded-full backdrop-blur-md transition-all duration-200 shadow-md ${
            isLiked
              ? "bg-red-500 text-white scale-105 hover:bg-red-600 shadow-red-500/30 ring-2 ring-red-400/50"
              : "bg-black/60 text-white/90 hover:bg-black/85 hover:scale-110 hover:text-red-400"
          }`}
        >
          <Heart className={`size-4 transition-transform duration-200 ${isLiked ? "fill-current scale-110" : ""}`} />
        </button>
      )}

      <button className="overflow-hidden bg-muted p-5 text-left" onClick={() => onSelect(book)} aria-label={`View ${book.title}`}>
        <BookCoverImage 
          isbn={book.isbn} 
          thumbnail={(book as any).thumbnail} 
          title={book.title} 
          author={book.author} 
          genre={book.genre}
          alt={`Cover of ${book.title}`} 
          className="mx-auto aspect-[2/3] h-64 rounded-md object-cover shadow-lg transition duration-500 group-hover:scale-[1.03]"
        />
      </button>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-col gap-1">
          <h3 className="font-serif text-lg leading-tight text-card-foreground line-clamp-2">{book.title}</h3>
          <p className="text-sm text-muted-foreground line-clamp-1">{book.author}</p>
        </div>
        <div className="mt-auto flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{book.genre}</span>
          <span className="flex items-center gap-1 font-semibold">
            <Star className="size-4 fill-accent text-accent" />
            {displayRating}
          </span>
        </div>
        <Button 
          variant="outline" 
          className="h-10 w-full group-hover:bg-primary group-hover:text-primary-foreground transition cursor-pointer font-medium text-sm" 
          onClick={() => onSelect(book)}
        >
          Discover similar
          <ArrowRight data-icon="inline-end" className="size-4 ml-1.5" />
        </Button>
      </div>
    </article>
  )
}

export function BookMindApp() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All')
  const [sortBy, setSortBy] = useState('recommended')
  const [selected, setSelected] = useState<Book | null>(null)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [apiBooks, setApiBooks] = useState<Book[]>(books)
  const [apiFilters, setApiFilters] = useState<string[]>(filters)
  const [isLoading, setIsLoading] = useState(false)
  const [isExternalSearch, setIsExternalSearch] = useState(false)
  const [searchStats, setSearchStats] = useState({ total: 0, local: 0, external: 0 })
  const [favorites, setFavorites] = useState<Book[]>([])
  const [showLikedModal, setShowLikedModal] = useState(false)
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [showGenreFilterModal, setShowGenreFilterModal] = useState(false)
  const [similarBooks, setSimilarBooks] = useState<(Book & { score?: number })[]>([])
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false)
  const [failedCovers, setFailedCovers] = useState<Set<string>>(new Set())
  const [displayLimit, setDisplayLimit] = useState(16)

  const handleCoverFailed = (bookKey: string) => {
    setFailedCovers(prev => {
      const next = new Set(prev)
      next.add(bookKey)
      return next
    })
  }

  // Suggestions state
  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([])
  const [showHeroSuggestions, setShowHeroSuggestions] = useState(false)
  const [showExploreSuggestions, setShowExploreSuggestions] = useState(false)
  const [activeSuggestIdx, setActiveSuggestIdx] = useState(-1)
  const heroSearchRef = useRef<HTMLDivElement>(null)
  const exploreSearchRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    try {
      const savedFavs = localStorage.getItem('bookmind-favorites');
      if (savedFavs) {
        setFavorites(JSON.parse(savedFavs));
      }
    } catch (e) {
      console.error('Failed to load favorites', e);
    }
  }, [])

  const toggleFavorite = (book: Book) => {
    setFavorites(prev => {
      const exists = prev.some(f => f.title === book.title);
      const next = exists ? prev.filter(f => f.title !== book.title) : [...prev, book];
      localStorage.setItem('bookmind-favorites', JSON.stringify(next));
      return next;
    });
  }

  const clearAllFavorites = () => {
    setFavorites([]);
    localStorage.removeItem('bookmind-favorites');
  }

  useEffect(() => {
    fetch('https://book-recommender-6cy9.onrender.com/categories', { headers: { 'Bypass-Tunnel-Reminder': 'true' } })
      .then(res => res.json())
      .then(data => { 
        if (data.categories && data.categories.length > 0) {
          setApiFilters(data.categories) 
        }
      })
      .catch(err => console.error('Could not connect to backend categories:', err))
      
    fetch('https://book-recommender-6cy9.onrender.com/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'popular', category: 'All', tone: 'All', limit: 120 })
    })
      .then(res => res.json())
      .then(data => {
        const booksList = data.books && data.books.length > 0 
          ? data.books 
          : [...(data.local_results || []), ...(data.external_results || [])];
        if (booksList && booksList.length > 0) {
           const valid = booksList.map((r: any) => ({
             title: r.title, author: r.authors, genre: r.genre || r.simple_categories || 'Literature',
             rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.0, isbn: r.isbn || '0', description: r.description, thumbnail: r.thumbnail, source: r.source || 'BookMind Library', links: r.links
           }));
           setApiBooks(valid.length > 0 ? valid : books)
           setIsExternalSearch(Boolean(data.external_results?.length > 0))
           setSearchStats({ total: valid.length, local: data.sources?.local || 0, external: data.sources?.google_books || 0 })
        }
      })
      .catch(err => console.error('Could not connect to backend recommend:', err))
  }, [])

  // Dynamic Live Search & Suggestion Query Fetcher
  useEffect(() => {
    const trimmed = query.trim()
    if (trimmed.length < 2) {
      setSuggestions([])
      setActiveSuggestIdx(-1)
      if (trimmed.length === 0 && query !== '') {
        handleSearch(undefined, category, 'popular')
      }
      return
    }

    const timer = setTimeout(() => {
      // 1. Instant local matches from fallback books
      const clientMatches: SuggestionItem[] = books
        .filter(b => b.title.toLowerCase().includes(trimmed.toLowerCase()) || b.author.toLowerCase().includes(trimmed.toLowerCase()))
        .map(b => ({
          title: b.title,
          author: b.author,
          genre: b.genre,
          thumbnail: cover(b.isbn, (b as any).thumbnail),
          isbn: b.isbn
        }))

      fetch(`https://book-recommender-6cy9.onrender.com/api/books/suggest?q=${encodeURIComponent(trimmed)}`, { headers: { 'Bypass-Tunnel-Reminder': 'true' } })
        .then(res => res.json())
        .then(data => {
          if (data.suggestions && data.suggestions.length > 0) {
            const combined: SuggestionItem[] = [...data.suggestions]
            clientMatches.forEach(cm => {
              if (!combined.some(item => item.title.toLowerCase() === cm.title.toLowerCase())) {
                combined.push(cm)
              }
            })
            setSuggestions(combined.slice(0, 8))
          } else {
            setSuggestions(clientMatches.slice(0, 8))
          }
        })
        .catch(() => {
          setSuggestions(clientMatches.slice(0, 8))
        })

      // 2. Automatically perform live search in background with active genre filters
      const activeGenresList = selectedGenres.length > 0 ? selectedGenres : (category && category !== 'All' ? [category] : []);
      const genresParam = encodeURIComponent(activeGenresList.join(','));

      fetch(`https://book-recommender-6cy9.onrender.com/api/books/search?q=${encodeURIComponent(trimmed)}&category=${encodeURIComponent(category)}&genres=${genresParam}`, { headers: { 'Bypass-Tunnel-Reminder': 'true' } })
        .then(res => res.json())
        .then(data => {
          const booksList = data.external_results?.length > 0 || data.local_results?.length > 0 
            ? [...(data.local_results || []), ...(data.external_results || [])]
            : [];
          if (booksList && booksList.length > 0) {
            setApiBooks(booksList.map((r: any) => ({
              title: r.title, author: r.authors, genre: r.genre || 'Literature',
              rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.5, isbn: r.isbn || '0', description: r.description, thumbnail: r.thumbnail,
              source: r.source, links: r.links
            })))
            setIsExternalSearch(Boolean(data.external_results?.length > 0))
            setSearchStats({ total: data.total_results || booksList.length, local: data.sources?.local || 0, external: data.sources?.google_books || 0 })
          }
        })
        .catch(() => {})
    }, 250)

    return () => clearTimeout(timer)
  }, [query, selectedGenres, category])

  // Click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (heroSearchRef.current && !heroSearchRef.current.contains(e.target as Node)) {
        setShowHeroSuggestions(false)
      }
      if (exploreSearchRef.current && !exploreSearchRef.current.contains(e.target as Node)) {
        setShowExploreSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleCategoryClick = (filter: string) => {
    setCategory(filter)
    setSelectedGenres([])
    setQuery('')
    setShowHeroSuggestions(false)
    setShowExploreSuggestions(false)
    setDisplayLimit(16)
    const targetGenres = filter === 'All' ? [] : [filter]
    handleSearch(undefined, filter, '', targetGenres)
  }

  const handleApplyGenres = (genres: string[]) => {
    setSelectedGenres(genres)
    setCategory('All')
    setIsLoading(true)
    setShowGenreFilterModal(false)
    setDisplayLimit(16)

    if (genres.length === 0) {
      handleSearch(undefined, 'All', 'popular', [])
      return
    }

    fetch('https://book-recommender-6cy9.onrender.com/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'popular', categories: genres, tone: 'All', limit: 120 })
    })
      .then(res => res.json())
      .then(data => {
        const booksList = data.books && data.books.length > 0
          ? data.books
          : [...(data.local_results || []), ...(data.external_results || [])];
        if (booksList.length > 0) {
          setApiBooks(booksList.map((r: any) => ({
            title: r.title, author: r.authors, genre: r.genre || r.simple_categories || (genres[0] || 'Literature'),
            rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.0,
            isbn: r.isbn || '0', description: r.description, thumbnail: r.thumbnail,
            source: r.source || 'BookMind Library', links: r.links
          })))
          setIsExternalSearch(Boolean(data.external_results?.length > 0))
          setSearchStats({ total: data.total_results || booksList.length, local: data.sources?.local || 0, external: data.sources?.google_books || 0 })
        } else {
          const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, genres))
          setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
        }
        setIsLoading(false)
        document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' })
      })
      .catch(err => {
        console.error(err)
        const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, genres))
        setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
        setIsLoading(false)
      })
  }

  const toggleGenre = (genreName: string) => {
    const next = selectedGenres.includes(genreName)
      ? selectedGenres.filter(g => g !== genreName)
      : [...selectedGenres, genreName]
    setSelectedGenres(next)
  }

  const handleSelectSuggestion = (suggestion: SuggestionItem) => {
    setQuery(suggestion.title)
    setShowHeroSuggestions(false)
    setShowExploreSuggestions(false)
    setActiveSuggestIdx(-1)
    setDisplayLimit(16)
    handleSearch(undefined, 'All', suggestion.title, [])
  }

  const handleSearch = (e?: React.FormEvent, overrideCat?: string, customQuery?: string, overrideGenres?: string[]) => {
    if (e) e.preventDefault()
    setShowHeroSuggestions(false)
    setShowExploreSuggestions(false)
    setActiveSuggestIdx(-1)
    setDisplayLimit(16)

    const currentQuery = customQuery !== undefined ? customQuery : query.trim()
    const currentCategory = overrideCat !== undefined ? overrideCat : category
    setIsLoading(true)

    const activeGenresList = overrideGenres !== undefined
      ? overrideGenres
      : (selectedGenres.length > 0 ? selectedGenres : (currentCategory && currentCategory !== 'All' ? [currentCategory] : []));
    const genresParam = encodeURIComponent(activeGenresList.join(','));

    if (currentQuery && currentQuery.toLowerCase() !== 'popular') {
        fetch(`https://book-recommender-6cy9.onrender.com/api/books/search?q=${encodeURIComponent(currentQuery)}&category=${encodeURIComponent(currentCategory)}&genres=${genresParam}&limit=120`, { headers: { 'Bypass-Tunnel-Reminder': 'true' } })
          .then(res => res.json())
          .then(data => {
             const booksList = data.books && data.books.length > 0
               ? data.books
               : [...(data.local_results || []), ...(data.external_results || [])];
             const isExternal = Boolean(data.external_results?.length > 0);
             if (booksList && booksList.length > 0) {
               setApiBooks(booksList.map((r: any) => ({
                 title: r.title, author: r.authors, genre: r.genre || 'Literature',
                 rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.0, isbn: r.isbn || '0', description: r.description, thumbnail: r.thumbnail,
                 source: r.source, links: r.links
               })))
               setIsExternalSearch(isExternal)
               setSearchStats({ total: data.total_results || booksList.length, local: data.sources?.local || 0, external: data.sources?.google_books || 0 })
             } else {
               const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, activeGenresList));
               setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
               setIsExternalSearch(false)
               setSearchStats({ total: books.length, local: books.length, external: 0 })
             }
             setIsLoading(false)
             document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' })
          })
          .catch(err => {
              console.error(err)
              const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, activeGenresList));
              setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
              setIsLoading(false)
          })
    } else {
        fetch('https://book-recommender-6cy9.onrender.com/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: 'popular', category: currentCategory, categories: activeGenresList, tone: 'All', limit: 120 })
        })
          .then(res => res.json())
          .then(data => {
            const booksList = data.books && data.books.length > 0
              ? data.books
              : [...(data.local_results || []), ...(data.external_results || [])];
            const isExternal = Boolean(data.external_results?.length > 0);
            if (booksList && booksList.length > 0) {
               const valid = booksList.map((r: any) => ({
                 title: r.title, author: r.authors, genre: r.genre || r.simple_categories || currentCategory,
                 rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.0, isbn: r.isbn || '0', description: r.description, thumbnail: r.thumbnail,
                 source: r.source || 'BookMind Library', links: r.links
               }));
               setApiBooks(valid)
               setIsExternalSearch(isExternal)
               setSearchStats({ total: data.total_results || booksList.length, local: data.sources?.local || 0, external: data.sources?.google_books || 0 })
            } else {
               const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, activeGenresList));
               setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
               setIsExternalSearch(false)
               setSearchStats({ total: books.length, local: books.length, external: 0 })
            }
            setIsLoading(false)
            document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' })
          })
          .catch(err => {
              console.error(err)
              const fallbackMatches = books.filter(b => isMatchingGenre(b.genre, activeGenresList));
              setApiBooks(fallbackMatches.length > 0 ? fallbackMatches : books)
              setIsLoading(false)
          })
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent, isHero: boolean) => {
    const isShowing = isHero ? showHeroSuggestions : showExploreSuggestions
    if (!isShowing || suggestions.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveSuggestIdx(prev => (prev < suggestions.length - 1 ? prev + 1 : 0))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveSuggestIdx(prev => (prev > 0 ? prev - 1 : suggestions.length - 1))
    } else if (e.key === 'Enter') {
      if (activeSuggestIdx >= 0 && activeSuggestIdx < suggestions.length) {
        e.preventDefault()
        handleSelectSuggestion(suggestions[activeSuggestIdx])
      }
    } else if (e.key === 'Escape') {
      setShowHeroSuggestions(false)
      setShowExploreSuggestions(false)
      setActiveSuggestIdx(-1)
    }
  }

  const allFilteredBooks = useMemo(() => {
    const activeGenresList = selectedGenres.length > 0
      ? selectedGenres
      : (category && category !== 'All' ? [category] : []);

    let list: Book[] = apiBooks.filter(b => {
      const bookKey = `${b.title}-${b.isbn || ''}`;
      if (failedCovers.has(bookKey)) return false;
      if (!isValidCover((b as any).thumbnail, b.isbn)) return false;
      if (isBestsellerTitle(b.title)) return false;
      if (activeGenresList.length > 0 && !isMatchingGenre(b.genre, activeGenresList)) return false;
      return true;
    });

    // Deduplicate by clean title to ensure 100% unique real books
    const seen = new Set<string>();
    const uniqueList: Book[] = [];
    for (const b of list) {
      const tKey = b.title.toLowerCase().trim();
      if (!seen.has(tKey)) {
        seen.add(tKey);
        uniqueList.push(b);
      }
    }

    // Apply active sorting
    if (sortBy === 'rating_desc') {
      uniqueList.sort((a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0));
    } else if (sortBy === 'rating_asc') {
      uniqueList.sort((a, b) => (Number(a.rating) || 0) - (Number(b.rating) || 0));
    } else if (sortBy === 'title_asc') {
      uniqueList.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortBy === 'title_desc') {
      uniqueList.sort((a, b) => b.title.localeCompare(a.title));
    }

    return uniqueList;
  }, [apiBooks, sortBy, selectedGenres, category, failedCovers])

  const visibleBooks = useMemo(() => {
    return allFilteredBooks.slice(0, displayLimit);
  }, [allFilteredBooks, displayLimit])

  const fetchSimilarBooksFor = (book: Book) => {
    setIsLoadingSimilar(true)
    fetch('https://book-recommender-6cy9.onrender.com/api/books/similar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: book.title,
        description: book.description || '',
        genre: book.genre || '',
        isbn: book.isbn || ''
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.recommendations && data.recommendations.length > 0) {
          setSimilarBooks(data.recommendations.map((r: any) => ({
            title: r.title,
            author: r.authors || r.author,
            genre: r.genre || 'Literature',
            rating: r.rating !== undefined && r.rating !== null ? Number(r.rating) : 4.5,
            isbn: r.isbn || '0',
            description: r.description,
            thumbnail: r.thumbnail,
            source: r.source || 'BookMind Library',
            links: r.links,
            score: r.score || 85
          })))
        }
        setIsLoadingSimilar(false)
      })
      .catch(() => {
        setIsLoadingSimilar(false)
      })
  }

  const selectBook = (book: Book) => {
    setSelected(book)
    setShowRecommendations(false)
    fetchSimilarBooksFor(book)
    setTimeout(() => document.getElementById('book-details')?.scrollIntoView({ behavior: 'smooth' }), 20)
  }

  const openRecommendations = () => {
    const target = selected ?? apiBooks[0]
    setSelected(target)
    if (target) {
      fetchSimilarBooksFor(target)
    }
    setShowRecommendations(true)
    setMenuOpen(false)
    window.setTimeout(() => document.getElementById('recommendations')?.scrollIntoView({ behavior: 'smooth' }), 50)
  }

  const recommendations = similarBooks.length > 0 
    ? similarBooks 
    : apiBooks.filter((book) => book.title !== selected?.title).slice(0, 5)

  return (
    <main className="min-h-screen overflow-x-hidden">
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 lg:px-8">
          <a href="#home" className="flex items-center gap-2 font-serif text-xl font-bold"><span className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground"><BookOpen className="size-5" /></span>BookMind</a>
          <nav className="hidden items-center gap-8 text-sm font-medium md:flex">
            <a href="#home">Home</a>
            <a href="#explore">Explore</a>
            <button type="button" onClick={openRecommendations} className="hover:text-accent-foreground">Recommendations</button>
            <button type="button" onClick={() => setShowLikedModal(true)} className="flex items-center gap-1.5 hover:text-red-500 transition">
              <Heart className={`size-4 ${favorites.length > 0 ? "fill-red-500 text-red-500" : ""}`} />
              Liked ({favorites.length})
            </button>
            <a href="#about">About</a>
          </nav>
          <div className="hidden items-center gap-3 md:flex">
            <Button 
              variant="outline" 
              className="relative flex items-center gap-2 h-10 px-3.5 border-border/80 hover:border-red-500/40 hover:text-red-500 transition" 
              onClick={() => setShowLikedModal(true)}
              aria-label="View Liked Books"
            >
              <Heart className={`size-4 ${favorites.length > 0 ? "fill-red-500 text-red-500" : "text-muted-foreground"}`} />
              <span className="font-medium text-sm">Liked Books</span>
              {favorites.length > 0 && (
                <span className="flex size-5 items-center justify-center rounded-full bg-red-500 text-[11px] font-bold text-white shadow-sm">
                  {favorites.length}
                </span>
              )}
            </Button>
            <Button className="h-10 px-4" onClick={() => document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' })}>Get Started</Button>
          </div>
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">{menuOpen ? <X /> : <Menu />}</Button>
        </div>
        {menuOpen && (
          <nav className="flex flex-col items-start gap-4 border-t border-border px-5 py-5 md:hidden bg-background">
            <a href="#home" onClick={() => setMenuOpen(false)}>Home</a>
            <a href="#explore" onClick={() => setMenuOpen(false)}>Explore</a>
            <button type="button" onClick={() => { setMenuOpen(false); openRecommendations(); }}>Recommendations</button>
            <button type="button" onClick={() => { setMenuOpen(false); setShowLikedModal(true); }} className="flex items-center gap-2 text-sm font-medium text-red-500">
              <Heart className="size-4 fill-current" />
              Liked Books ({favorites.length})
            </button>
            <a href="#about" onClick={() => setMenuOpen(false)}>About</a>
          </nav>
        )}
      </header>

      <section id="home" className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-20 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:py-28">
        <div className="flex flex-col items-start gap-7">
          <p className="flex items-center gap-2 text-xs font-bold tracking-[.2em] text-accent-foreground"><Sparkles className="size-4" />AI-POWERED BOOK DISCOVERY</p>
          <div className="flex flex-col gap-5"><h1 className="max-w-2xl text-balance font-serif text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">Discover Your Next Great <span className="text-accent-foreground">Read.</span></h1><p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">Find books that match your interests using intelligent semantic recommendations.</p></div>
          
          {/* Hero Search Box with Autocomplete */}
          <div ref={heroSearchRef} className="relative w-full max-w-2xl">
            <form className="flex w-full flex-col gap-3 rounded-2xl bg-card p-2 shadow-lg sm:flex-row border border-border/80" onSubmit={handleSearch}>
              <label className="flex flex-1 items-center gap-3 px-3">
                <Search className="size-5 text-muted-foreground" />
                <span className="sr-only">Search books</span>
                <input 
                  value={query} 
                  onChange={(e) => {
                    setQuery(e.target.value)
                    setShowHeroSuggestions(true)
                  }}
                  onFocus={() => {
                    if (query.trim().length >= 2) setShowHeroSuggestions(true)
                  }}
                  onKeyDown={(e) => handleKeyDown(e, true)}
                  placeholder="Search books, authors, keywords (e.g. atom)..." 
                  className="h-12 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground" 
                />
              </label>
              <Button className="h-12 px-7" type="submit">Search</Button>
            </form>

            {/* Suggestions Popover */}
            {showHeroSuggestions && suggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 z-50 rounded-2xl border border-border bg-card/95 backdrop-blur-md shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="p-2 border-b border-border/60 bg-muted/30 px-4 py-2 flex items-center justify-between text-xs text-muted-foreground font-medium">
                  <span className="flex items-center gap-1.5"><Sparkles className="size-3.5 text-accent-foreground" /> Book Suggestions</span>
                  <span>Press ↑ ↓ to navigate, Enter to select</span>
                </div>
                <div className="max-h-80 overflow-y-auto divide-y divide-border/40">
                  {suggestions.map((item, idx) => (
                    <button
                      key={`${item.title}-${idx}`}
                      type="button"
                      onClick={() => handleSelectSuggestion(item)}
                      onMouseEnter={() => setActiveSuggestIdx(idx)}
                      className={`w-full flex items-center gap-3.5 p-3 text-left transition duration-150 ${
                        activeSuggestIdx === idx ? 'bg-accent/15' : 'hover:bg-muted/60'
                      }`}
                    >
                      <div className="size-10 shrink-0 overflow-hidden rounded-md bg-muted border border-border/50">
                        <BookCoverImage 
                          isbn={item.isbn} 
                          thumbnail={item.thumbnail} 
                          title={item.title} 
                          author={item.author} 
                          genre={item.genre} 
                          alt={item.title} 
                          className="h-full w-full object-cover" 
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-serif text-sm font-medium text-foreground truncate">
                          <HighlightMatch text={item.title} highlight={query} />
                        </p>
                        <p className="text-xs text-muted-foreground truncate">{item.author}</p>
                      </div>
                      <span className="shrink-0 rounded-full bg-secondary/80 px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground">
                        {item.genre}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-sm"><span className="text-muted-foreground">Popular:</span>{apiFilters.slice(1, 6).map((tag) => <button key={tag} onClick={() => handleCategoryClick(tag)} className="rounded-full border border-border bg-card px-3 py-1.5 transition hover:border-accent hover:text-accent-foreground">{tag}</button>)}</div>
        </div>
        <div className="relative mx-auto hidden h-[520px] w-full max-w-xl sm:block" aria-label="Featured book covers">
          <BookCoverImage 
            isbn={apiBooks[0]?.isbn || books[0].isbn} 
            thumbnail={(apiBooks[0] as any)?.thumbnail || (books[0] as any)?.thumbnail} 
            title={apiBooks[0]?.title || books[0].title} 
            author={apiBooks[0]?.author || books[0].author} 
            genre={apiBooks[0]?.genre || books[0].genre} 
            alt="Featured book cover" 
            className="absolute left-[8%] top-20 aspect-[2/3] w-[38%] -rotate-6 rounded-lg object-cover shadow-2xl" 
          />
          <BookCoverImage 
            isbn={apiBooks[1]?.isbn || books[1].isbn} 
            thumbnail={(apiBooks[1] as any)?.thumbnail || (books[1] as any)?.thumbnail} 
            title={apiBooks[1]?.title || books[1].title} 
            author={apiBooks[1]?.author || books[1].author} 
            genre={apiBooks[1]?.genre || books[1].genre} 
            alt="Featured book cover" 
            className="absolute left-[32%] top-0 aspect-[2/3] w-[40%] rotate-2 rounded-lg object-cover shadow-2xl" 
          />
          <BookCoverImage 
            isbn={apiBooks[2]?.isbn || books[2].isbn} 
            thumbnail={(apiBooks[2] as any)?.thumbnail || (books[2] as any)?.thumbnail} 
            title={apiBooks[2]?.title || books[2].title} 
            author={apiBooks[2]?.author || books[2].author} 
            genre={apiBooks[2]?.genre || books[2].genre} 
            alt="Featured book cover" 
            className="absolute bottom-0 right-[3%] aspect-[2/3] w-[38%] rotate-6 rounded-lg object-cover shadow-2xl" 
          />
          <div className="absolute bottom-5 left-3 rounded-2xl border border-border bg-card p-4 shadow-xl">
            <p className="text-xs font-bold tracking-wider text-accent-foreground">CURATED BY AI</p>
            <p className="mt-1 font-serif text-lg">Stories chosen for you</p>
          </div>
        </div>
      </section>

      <section id="explore" className="bg-secondary/60 py-20"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 lg:px-8"><div className="flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><p className="mb-3 text-xs font-bold tracking-[.2em] text-accent-foreground">THE LIBRARY</p><h2 className="font-serif text-4xl font-semibold">Explore Our Book Collection</h2><p className="mt-3 text-muted-foreground">Browse our collection and find a book that catches your interest.</p></div><select aria-label="Sort books" value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="h-11 rounded-xl border border-border bg-card px-4 text-sm font-medium outline-none cursor-pointer hover:border-accent transition"><option value="recommended">Sort by: Recommended</option><option value="rating_desc">Rating: High to low</option><option value="rating_asc">Rating: Low to high</option><option value="title_asc">Title: A–Z</option><option value="title_desc">Title: Z–A</option></select></div>
        
        <div className="flex flex-col gap-4">
          {/* Explore Search Box with Autocomplete */}
          <div ref={exploreSearchRef} className="relative max-w-md">
            <label className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 focus-within:ring-2 focus-within:ring-primary/20">
              <Search className="size-4 text-muted-foreground" />
              <span className="sr-only">Search collection</span>
              <input 
                value={query} 
                onChange={(e) => {
                  setQuery(e.target.value)
                  setShowExploreSuggestions(true)
                }}
                onFocus={() => {
                  if (query.trim().length >= 2) setShowExploreSuggestions(true)
                }}
                onKeyDown={(e) => handleKeyDown(e, false)}
                placeholder="Search books (e.g. atom)..." 
                className="h-11 flex-1 bg-transparent outline-none text-sm" 
              />
              {query && (
                <button type="button" onClick={() => { setQuery(''); setSuggestions([]); }} className="text-muted-foreground hover:text-foreground">
                  <X className="size-4" />
                </button>
              )}
            </label>

            {/* Explore Suggestions Popover */}
            {showExploreSuggestions && suggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 z-50 rounded-2xl border border-border bg-card/95 backdrop-blur-md shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="p-2 border-b border-border/60 bg-muted/30 px-3 py-1.5 flex items-center justify-between text-[11px] text-muted-foreground font-medium">
                  <span className="flex items-center gap-1"><BookText className="size-3 text-accent-foreground" /> Suggestions</span>
                </div>
                <div className="max-h-64 overflow-y-auto divide-y divide-border/40">
                  {suggestions.map((item, idx) => (
                    <button
                      key={`exp-${item.title}-${idx}`}
                      type="button"
                      onClick={() => handleSelectSuggestion(item)}
                      onMouseEnter={() => setActiveSuggestIdx(idx)}
                      className={`w-full flex items-center gap-3 p-2.5 text-left transition duration-150 ${
                        activeSuggestIdx === idx ? 'bg-accent/15' : 'hover:bg-muted/60'
                      }`}
                    >
                      <div className="size-8 shrink-0 overflow-hidden rounded bg-muted border border-border/50">
                        <BookCoverImage 
                          isbn={item.isbn} 
                          thumbnail={item.thumbnail} 
                          title={item.title} 
                          author={item.author} 
                          genre={item.genre} 
                          alt={item.title} 
                          className="h-full w-full object-cover" 
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-serif text-xs font-medium text-foreground truncate">
                          <HighlightMatch text={item.title} highlight={query} />
                        </p>
                        <p className="text-[10px] text-muted-foreground truncate">{item.author}</p>
                      </div>
                      <span className="shrink-0 rounded-full bg-secondary/80 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                        {item.genre}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              {/* Multi-Genre Filter Button */}
              <Button
                variant="outline"
                type="button"
                onClick={() => setShowGenreFilterModal(true)}
                className={`flex items-center gap-2 h-10 px-4 rounded-full border transition cursor-pointer shadow-sm ${
                  selectedGenres.length > 0
                    ? 'border-accent bg-accent/20 text-accent-foreground font-semibold ring-1 ring-accent/40'
                    : 'border-border bg-card hover:border-accent text-foreground'
                }`}
              >
                <SlidersHorizontal className="size-4 text-accent" />
                <span>Filter by Genres</span>
                {selectedGenres.length > 0 && (
                  <span className="flex size-5 items-center justify-center rounded-full bg-accent text-[11px] font-bold text-accent-foreground">
                    {selectedGenres.length}
                  </span>
                )}
              </Button>

              <button
                type="button"
                onClick={() => setShowLikedModal(true)}
                className={`rounded-full px-4 py-2 text-sm font-medium transition flex items-center gap-1.5 border shadow-sm ${
                  favorites.length > 0
                    ? 'border-red-500/50 bg-red-500/10 text-red-500 hover:bg-red-500/20'
                    : 'border-border bg-card text-muted-foreground hover:border-accent'
                }`}
              >
                <Heart className={`size-3.5 ${favorites.length > 0 ? 'fill-current text-red-500' : ''}`} />
                Liked Books ({favorites.length})
              </button>
              
              <Button
                variant="outline"
                className="h-9 rounded-full px-4 border border-border bg-card hover:border-emerald-500 hover:text-emerald-600 transition flex items-center gap-1.5 shadow-sm text-sm"
                onClick={() => {
                  const genreTarget = selectedGenres.length === 1 ? selectedGenres[0] : (category && category !== 'All' ? category : 'Classics');
                  window.open(`https://www.gutenberg.org/ebooks/search/?query=${encodeURIComponent(genreTarget)}`, '_blank', 'noopener,noreferrer');
                }}
              >
                <BookOpen className="size-3.5 text-emerald-500" />
                Browse Free {selectedGenres.length === 1 ? selectedGenres[0] : (category && category !== 'All' ? category : 'Classics')}
              </Button>
              {apiFilters.slice(0, 8).map((filter) => (
                <button 
                  key={filter} 
                  onClick={() => handleCategoryClick(filter)} 
                  className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                    category === filter && selectedGenres.length === 0 ? 'bg-primary text-primary-foreground' : 'border border-border bg-card hover:border-accent'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            {/* Active Selected Genre Chips */}
            {selectedGenres.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 pt-1 animate-in fade-in duration-150">
                <span className="text-xs font-semibold text-muted-foreground">Active Genres:</span>
                {selectedGenres.map(g => (
                  <button
                    key={g}
                    type="button"
                    onClick={() => {
                      const updated = selectedGenres.filter(item => item !== g)
                      handleApplyGenres(updated)
                    }}
                    className="group flex items-center gap-1.5 rounded-full bg-accent/15 border border-accent/40 px-3 py-1 text-xs font-medium text-accent-foreground hover:bg-red-500/10 hover:border-red-500/40 hover:text-red-500 transition"
                  >
                    <span>{g}</span>
                    <X className="size-3 text-muted-foreground group-hover:text-red-500" />
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => handleApplyGenres([])}
                  className="text-xs text-muted-foreground hover:text-foreground underline ml-1"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
        </div>
        {query && <div className="flex flex-col gap-1"><p className="font-serif text-xl">Search results for “{query}”</p>{!isLoading && <p className="font-sans text-sm text-muted-foreground">{visibleBooks.length} books found in BookMind Library</p>}</div>}
        {isLoading && (
          <div className="flex flex-col gap-6">
            <p className="flex items-center gap-2 text-sm text-muted-foreground"><span className="size-4 animate-spin rounded-full border-2 border-accent border-r-transparent" /> Searching BookMind Library...</p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 16 }).map((_, i) => (
                <div key={i} className="flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm animate-pulse">
                  <div className="aspect-[2/3] h-64 w-full bg-muted/60" />
                  <div className="flex flex-1 flex-col gap-3 p-5">
                    <div className="h-5 w-3/4 rounded bg-muted/70" />
                    <div className="h-4 w-1/2 rounded bg-muted/50" />
                    <div className="mt-auto flex justify-between pt-4">
                      <div className="h-4 w-1/4 rounded bg-muted/50" />
                      <div className="h-4 w-1/4 rounded bg-muted/50" />
                    </div>
                    <div className="h-10 w-full rounded bg-muted/40" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!isLoading && visibleBooks.length > 0 && (
          <div className="flex flex-col gap-8">
            <div className="book-grid grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {visibleBooks.map((book, idx) => (
                <BookCard 
                  key={`${book.title}-${book.isbn || ''}-${idx}`} 
                  book={book} 
                  onSelect={selectBook} 
                  isLiked={favorites.some(f => f.title === book.title)}
                  onToggleLike={toggleFavorite}
                  onCoverFailed={handleCoverFailed}
                />
              ))}
            </div>

            {/* More Button: Removed after 24 tiles load */}
            {displayLimit < 24 && displayLimit < allFilteredBooks.length && (
              <div className="flex flex-col items-center justify-center pt-4">
                <Button
                  type="button"
                  onClick={() => setDisplayLimit(prev => prev + 8)}
                  size="lg"
                  className="group relative flex items-center gap-2 h-11 px-8 rounded-full bg-primary text-primary-foreground font-semibold shadow-md hover:shadow-lg hover:scale-[1.02] transition duration-200 cursor-pointer text-sm"
                >
                  <span>More</span>
                  <ChevronDown className="size-4 transition-transform duration-200 group-hover:translate-y-0.5" />
                </Button>
              </div>
            )}
          </div>
        )}
        {!isLoading && visibleBooks.length === 0 && (
          <div className="flex flex-col items-center gap-4 rounded-3xl border border-border bg-card px-6 py-16 text-center">
            <Sparkles className="size-10 text-accent-foreground animate-pulse" />
            <h3 className="font-serif text-2xl font-semibold">No books found for the selected genre</h3>
            <p className="text-muted-foreground max-w-md text-sm">
              We couldn't find any books matching your strict genre filter. Try exploring other genres or adjusting your search.
            </p>
            <div className="flex gap-3">
              <Button onClick={() => { setQuery(''); setCategory('All'); handleSearch(undefined, 'All', 'popular'); }}>
                Browse All Books
              </Button>
            </div>
          </div>
        )}
      </div></section>

      {selected && <section id="book-details" className="mx-auto max-w-6xl px-5 py-20 lg:px-8"><div className="grid gap-10 rounded-3xl border border-border bg-card p-6 shadow-xl md:grid-cols-[280px_1fr] md:p-10"><BookCoverImage isbn={selected.isbn} thumbnail={(selected as any).thumbnail} title={selected.title} author={selected.author} genre={selected.genre} alt={`Cover of ${selected.title}`} className="mx-auto aspect-[2/3] w-full max-w-[280px] rounded-lg object-cover shadow-xl" /><div className="flex flex-col justify-center gap-5"><div><p className="mb-2 text-sm font-semibold text-accent-foreground">{selected.genre} · BookMind Library</p><h2 className="text-balance font-serif text-4xl font-semibold md:text-5xl">{selected.title}</h2><p className="mt-2 text-lg text-muted-foreground">{selected.author}</p></div><div className="flex items-center gap-2 font-semibold text-accent-foreground"><div className="flex items-center text-amber-500">{Array.from({ length: 5 }).map((_, i) => (<Star key={i} className={`size-4 ${i < Math.round(Number(selected.rating) || 4.5) ? 'fill-accent text-accent' : 'text-muted-foreground/30'}`} />))}</div><span className="text-foreground">{typeof selected.rating === 'number' ? selected.rating.toFixed(1) : selected.rating}</span><span className="text-xs text-muted-foreground font-normal">/ 5.0</span></div><p className="max-w-2xl leading-relaxed text-muted-foreground">{selected.description}</p><div className="flex flex-wrap gap-2">{[selected.genre, 'Recommended', 'Curated'].map((tag, tIdx) => <span key={`${tag}-${tIdx}`} className="rounded-full bg-secondary px-3 py-1.5 text-sm">{tag}</span>)}</div><div className="flex flex-col gap-6 w-full"><div className="flex flex-col gap-3 sm:flex-row"><Button className="h-12 px-6 shadow-md" onClick={() => { fetchSimilarBooksFor(selected); setShowRecommendations(true); setTimeout(() => document.getElementById('recommendations')?.scrollIntoView({ behavior: 'smooth' }), 50) }}>Find Similar Books<ArrowRight className="ml-2 size-4" /></Button><Button variant="outline" className={`h-12 px-6 shadow-sm ${favorites.some(f => f.title === selected.title) ? 'text-red-500 border-red-500 bg-red-500/10' : ''}`} onClick={() => toggleFavorite(selected)}><Heart className={`mr-2 size-4 ${favorites.some(f => f.title === selected.title) ? 'fill-current' : ''}`} />{favorites.some(f => f.title === selected.title) ? 'Saved to Favorites' : 'Add to Favorites'}</Button></div><div className="rounded-2xl bg-secondary/30 border border-border p-5 w-full"><p className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider flex items-center gap-2"><BookText className="size-4 text-accent" /> Where to find this book</p><div className="flex flex-wrap gap-3"><a href={`https://openlibrary.org/search?q=${encodeURIComponent(selected.title + ' ' + selected.author)}`} target="_blank" rel="noopener noreferrer" className={`${buttonVariants({ variant: "default" })} h-10 bg-emerald-600 hover:bg-emerald-700 text-white font-medium`}>Read Free on Open Library ↗</a><a href={`https://www.google.com/search?tbm=bks&q=${encodeURIComponent(selected.title + ' ' + selected.author)}`} target="_blank" rel="noopener noreferrer" className={`${buttonVariants({ variant: "outline" })} h-10 border-border bg-card hover:border-accent/40`}>Google Books ↗</a><a href={`https://www.goodreads.com/search?q=${encodeURIComponent(selected.title)}`} target="_blank" rel="noopener noreferrer" className={`${buttonVariants({ variant: "outline" })} h-10 border-border bg-card hover:border-accent/40`}>Goodreads ↗</a><a href={`https://www.amazon.com/s?k=${encodeURIComponent(selected.title + ' book')}`} target="_blank" rel="noopener noreferrer" className={`${buttonVariants({ variant: "outline" })} h-10 border-border bg-card hover:border-accent/40`}>Amazon ↗</a></div></div></div></div></div></section>}

      {selected && showRecommendations && <section id="recommendations" className="bg-primary py-20 text-primary-foreground"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 lg:px-8"><div><p className="mb-3 flex items-center gap-2 text-xs font-bold tracking-[.2em] text-accent"><Sparkles className="size-4" />AI SEMANTIC MATCH</p><h2 className="font-serif text-4xl font-semibold">Books You Might Love</h2><p className="mt-3 text-primary-foreground/70">Based on themes, genre, and style of “{selected.title}”</p></div><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-5">{recommendations.map((book, index) => { const score = (book as any).score || ([92, 87, 84, 79, 75][index] || 75); return <article key={`${book.title}-${book.isbn || ''}-${index}`} onClick={() => selectBook(book)} className="overflow-hidden rounded-2xl bg-card text-card-foreground cursor-pointer transition hover:-translate-y-1 hover:shadow-xl"><BookCoverImage isbn={book.isbn} thumbnail={(book as any).thumbnail} title={book.title} author={book.author} genre={book.genre} alt={`Cover of ${book.title}`} className="aspect-[2/3] w-full object-cover" /><div className="flex flex-col gap-3 p-4"><div><h3 className="font-serif text-lg leading-tight line-clamp-1">{book.title}</h3><p className="mt-1 text-sm text-muted-foreground line-clamp-1">{book.author}</p></div><div className="flex items-center justify-between text-xs"><span>{book.genre}</span><strong className="text-accent-foreground">AI Match {score}%</strong></div><div className="h-1.5 overflow-hidden rounded-full bg-secondary"><div className="h-full rounded-full bg-accent" style={{ width: `${score}%` }} /></div></div></article>})}</div><div className="flex max-w-3xl items-start gap-4 rounded-2xl bg-primary-foreground/10 p-6"><Sparkles className="mt-1 size-5 shrink-0 text-accent" /><div><h3 className="font-serif text-xl">Books You'll Love to Read</h3><p className="mt-2 leading-relaxed text-primary-foreground/70">Personalized book recommendations matching the plot, themes, tone, and writing style of stories you love to read.</p></div></div></div></section>}

      {/* Multi-Genre Filter Modal */}
      {showGenreFilterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl max-h-[85vh] flex flex-col rounded-3xl border border-border bg-card shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-border p-6 bg-muted/30">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-xl bg-accent/20 text-accent-foreground border border-accent/30">
                  <SlidersHorizontal className="size-5" />
                </div>
                <div>
                  <h2 className="font-serif text-2xl font-semibold">Filter by Genres</h2>
                  <p className="text-xs text-muted-foreground">
                    Select multiple genres to find books combining your interests
                  </p>
                </div>
              </div>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => setShowGenreFilterModal(false)}
                className="rounded-full"
              >
                <X className="size-5" />
              </Button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
              {/* Quick Presets */}
              <div className="flex flex-col gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Popular Combinations:</span>
                <div className="flex flex-wrap gap-2">
                  {[
                    { label: '🚀 Sci-Fi & Fantasy', genres: ['Science Fiction', 'Fantasy'] },
                    { label: '🕵️ Mystery & Thriller', genres: ['Mystery', 'Thriller'] },
                    { label: '🧠 Mind & Psychology', genres: ['Nonfiction', 'Psychology', 'Self Development'] },
                    { label: '👶 Kids & Family', genres: ["Children's Fiction", "Children's Nonfiction"] },
                    { label: '📖 Classic Literature', genres: ['Fiction', 'History', 'Philosophy'] }
                  ].map(preset => (
                    <button
                      key={preset.label}
                      type="button"
                      onClick={() => handleApplyGenres(preset.genres)}
                      className="rounded-full border border-border bg-background px-3 py-1.5 text-xs font-medium hover:border-accent hover:text-accent-foreground transition cursor-pointer"
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Genre Badges Grid */}
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Select Genres:</span>
                  <span className="text-xs font-medium text-accent-foreground">{selectedGenres.length} selected</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  {ALL_GENRES.map((genre) => {
                    const isSelected = selectedGenres.includes(genre);
                    return (
                      <button
                        key={genre}
                        type="button"
                        onClick={() => toggleGenre(genre)}
                        className={`flex items-center justify-between p-3 rounded-xl border text-sm font-medium transition text-left cursor-pointer ${
                          isSelected
                            ? 'border-accent bg-accent/20 text-accent-foreground shadow-sm ring-1 ring-accent/40 font-semibold'
                            : 'border-border bg-background text-foreground hover:border-accent/60 hover:bg-muted/40'
                        }`}
                      >
                        <span className="truncate">{genre}</span>
                        <div className={`flex size-5 shrink-0 items-center justify-center rounded-md border ${
                          isSelected 
                            ? 'border-accent bg-accent text-accent-foreground' 
                            : 'border-border/80 bg-muted/40'
                        }`}>
                          {isSelected && <Check className="size-3.5 stroke-[3]" />}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="border-t border-border p-4 bg-muted/20 flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedGenres([])}
                disabled={selectedGenres.length === 0}
                className="text-xs text-muted-foreground hover:text-red-500"
              >
                Clear All
              </Button>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowGenreFilterModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={() => handleApplyGenres(selectedGenres)}
                  className="px-5 font-semibold"
                >
                  Apply ({selectedGenres.length})
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Liked Books Modal / Slide-over */}
      {showLikedModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-3xl max-h-[85vh] flex flex-col rounded-3xl border border-border bg-card shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-border p-6 bg-muted/30">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-xl bg-red-500/10 text-red-500 border border-red-500/20">
                  <Heart className="size-5 fill-current" />
                </div>
                <div>
                  <h2 className="font-serif text-2xl font-semibold">Your Liked Books</h2>
                  <p className="text-xs text-muted-foreground">
                    {favorites.length} {favorites.length === 1 ? 'book' : 'books'} saved in your reading list
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {favorites.length > 0 && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={clearAllFavorites}
                    className="text-xs text-muted-foreground hover:text-red-500"
                  >
                    Clear All
                  </Button>
                )}
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => setShowLikedModal(false)}
                  className="rounded-full"
                >
                  <X className="size-5" />
                </Button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              {favorites.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
                  <div className="flex size-16 items-center justify-center rounded-full bg-red-500/10 text-red-500 border border-red-500/20">
                    <Heart className="size-8 text-red-500" />
                  </div>
                  <h3 className="font-serif text-xl font-medium">No liked books yet</h3>
                  <p className="max-w-md text-sm text-muted-foreground">
                    Click the heart icon <Heart className="inline size-3.5 fill-red-500 text-red-500 mx-0.5" /> on any book cover to save books you love or want to read later.
                  </p>
                  <Button 
                    onClick={() => {
                      setShowLikedModal(false);
                      document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="mt-2"
                  >
                    Explore Library
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {favorites.map((book, idx) => (
                    <div 
                      key={`liked-${book.title}-${idx}`} 
                      className="flex gap-4 p-3.5 rounded-2xl border border-border bg-background hover:border-accent/60 transition group relative"
                    >
                      <BookCoverImage 
                        isbn={book.isbn} 
                        thumbnail={(book as any).thumbnail} 
                        title={book.title} 
                        author={book.author} 
                        genre={book.genre} 
                        alt={book.title} 
                        className="aspect-[2/3] w-20 rounded-lg object-cover shadow-md shrink-0 bg-muted" 
                      />
                      <div className="flex flex-1 flex-col justify-between min-w-0">
                        <div>
                          <span className="text-[11px] font-medium text-muted-foreground">{book.genre}</span>
                          <h4 className="font-serif text-base font-semibold leading-tight truncate text-foreground mt-0.5">
                            {book.title}
                          </h4>
                          <p className="text-xs text-muted-foreground truncate">{book.author}</p>
                          <div className="flex items-center gap-1 mt-1 text-xs font-semibold text-accent-foreground">
                            <Star className="size-3.5 fill-accent text-accent" />
                            <span>{typeof book.rating === 'number' ? book.rating.toFixed(1) : (book.rating || '4.5')}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-3">
                          <Button 
                            size="sm" 
                            className="h-8 text-xs flex-1"
                            onClick={() => {
                              setSelected(book);
                              setShowLikedModal(false);
                              setTimeout(() => document.getElementById('book-details')?.scrollIntoView({ behavior: 'smooth' }), 50);
                            }}
                          >
                            View Book
                          </Button>
                          <button
                            type="button"
                            onClick={() => toggleFavorite(book)}
                            aria-label={`Remove ${book.title} from liked`}
                            title="Remove from liked"
                            className="flex size-8 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground hover:text-red-500 hover:border-red-500/40 transition"
                          >
                            <Heart className="size-4 fill-red-500 text-red-500" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            {favorites.length > 0 && (
              <div className="border-t border-border p-4 bg-muted/20 flex items-center justify-between text-xs text-muted-foreground">
                <span>Books saved to your local reading list</span>
                <Button variant="outline" size="sm" onClick={() => setShowLikedModal(false)}>
                  Close
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      <footer id="about" className="border-t border-border"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 py-14 lg:px-8"><div className="flex flex-col justify-between gap-8 md:flex-row"><div><div className="flex items-center gap-2 font-serif text-xl font-bold"><BookOpen className="size-5" />BookMind</div><p className="mt-3 text-sm text-muted-foreground">Discover books. Explore ideas. Find your next story.</p></div><nav className="flex flex-wrap items-center gap-6 text-sm"><a href="#about">About</a><a href="#explore">Explore</a><button type="button" onClick={openRecommendations}>Recommendations</button><a href="#">GitHub</a></nav></div><p className="border-t border-border pt-7 text-sm text-muted-foreground">© 2026 BookMind — AI-Powered Book Recommendation System</p></div></footer>
    </main>
  )
}
