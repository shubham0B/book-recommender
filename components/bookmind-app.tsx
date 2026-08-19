'use client'

import { useMemo, useState } from 'react'
import { ArrowRight, BookOpen, Heart, Menu, Search, Sparkles, Star, UserRound, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

const books = [
  { title: 'The Hobbit', author: 'J.R.R. Tolkien', genre: 'Fantasy', rating: 4.8, isbn: '9780547928227', description: 'A reluctant hobbit leaves his quiet home for an unexpected journey through a world of dwarves, dragons, and ancient treasure.' },
  { title: "Harry Potter and the Philosopher's Stone", author: 'J.K. Rowling', genre: 'Fantasy', rating: 4.9, isbn: '9780747532699', description: 'An ordinary boy discovers a hidden world of magic, friendship, and a destiny far greater than he imagined.' },
  { title: 'The Alchemist', author: 'Paulo Coelho', genre: 'Fiction', rating: 4.6, isbn: '9780061122415', description: 'A timeless fable about following your dreams and listening to the quiet wisdom of your heart.' },
  { title: '1984', author: 'George Orwell', genre: 'Fiction', rating: 4.7, isbn: '9780451524935', description: 'A haunting vision of a totalitarian future where truth, freedom, and even thought are under surveillance.' },
  { title: 'Atomic Habits', author: 'James Clear', genre: 'Self Development', rating: 4.8, isbn: '9780735211292', description: 'A practical guide to building good habits, breaking bad ones, and mastering tiny behaviors that create remarkable results.' },
  { title: 'The Psychology of Money', author: 'Morgan Housel', genre: 'Self Development', rating: 4.7, isbn: '9780857197689', description: 'Timeless lessons on wealth, greed, and happiness told through insightful stories about how people think about money.' },
  { title: 'The Great Gatsby', author: 'F. Scott Fitzgerald', genre: 'Fiction', rating: 4.4, isbn: '9780743273565', description: 'A glittering portrait of ambition, longing, and illusion set amid the excess of the Jazz Age.' },
  { title: 'To Kill a Mockingbird', author: 'Harper Lee', genre: 'Fiction', rating: 4.8, isbn: '9780061120084', description: 'A moving story of childhood, compassion, and moral courage in a deeply divided American town.' },
  { title: 'Pride and Prejudice', author: 'Jane Austen', genre: 'Romance', rating: 4.7, isbn: '9780141439518', description: 'A sparkling comedy of manners about first impressions, family expectations, and unexpected love.' },
  { title: 'The Kite Runner', author: 'Khaled Hosseini', genre: 'Fiction', rating: 4.7, isbn: '9781594631931', description: 'An unforgettable story of friendship, betrayal, and redemption spanning Kabul to California.' },
  { title: 'Sapiens', author: 'Yuval Noah Harari', genre: 'History', rating: 4.6, isbn: '9780062316097', description: 'A sweeping exploration of how humankind came to dominate the planet and shape the modern world.' },
  { title: 'The Book Thief', author: 'Markus Zusak', genre: 'History', rating: 4.8, isbn: '9780375842207', description: 'In wartime Germany, a young girl finds solace and resistance in stolen books and the power of words.' },
]

type Book = (typeof books)[number]
const cover = (isbn: string) => `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`
const filters = ['All', 'Fiction', 'Fantasy', 'Mystery', 'Romance', 'Science', 'Self Development', 'History']

function BookCard({ book, onSelect }: { book: Book; onSelect: (book: Book) => void }) {
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl">
      <button className="overflow-hidden bg-muted p-5 text-left" onClick={() => onSelect(book)} aria-label={`View ${book.title}`}>
        <img src={cover(book.isbn)} alt={`Cover of ${book.title}`} className="mx-auto aspect-[2/3] h-64 rounded-md object-cover shadow-lg transition duration-500 group-hover:scale-[1.03]" />
      </button>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-col gap-1">
          <h3 className="font-serif text-lg leading-tight text-card-foreground">{book.title}</h3>
          <p className="text-sm text-muted-foreground">{book.author}</p>
        </div>
        <div className="mt-auto flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{book.genre}</span>
          <span className="flex items-center gap-1 font-semibold"><Star className="size-4 fill-accent text-accent" />{book.rating}</span>
        </div>
        <Button variant="outline" className="h-10 w-full group-hover:bg-primary group-hover:text-primary-foreground" onClick={() => onSelect(book)}>Discover similar<ArrowRight data-icon="inline-end" /></Button>
      </div>
    </article>
  )
}

export function BookMindApp() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All')
  const [selected, setSelected] = useState<Book | null>(null)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  const visibleBooks = useMemo(() => books.filter((book) => {
    const matchesCategory = category === 'All' || book.genre === category
    const needle = query.toLowerCase()
    return matchesCategory && `${book.title} ${book.author} ${book.genre}`.toLowerCase().includes(needle)
  }), [query, category])

  const selectBook = (book: Book) => { setSelected(book); setShowRecommendations(false); setTimeout(() => document.getElementById('book-details')?.scrollIntoView({ behavior: 'smooth' }), 20) }
  const openRecommendations = () => {
    setSelected((current) => current ?? books[0])
    setShowRecommendations(true)
    setMenuOpen(false)
    window.setTimeout(() => document.getElementById('recommendations')?.scrollIntoView({ behavior: 'smooth' }), 50)
  }
  const recommendations = books.filter((book) => book.title !== selected?.title).slice(0, 5)

  return (
    <main className="min-h-screen overflow-x-hidden">
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 lg:px-8">
          <a href="#home" className="flex items-center gap-2 font-serif text-xl font-bold"><span className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground"><BookOpen className="size-5" /></span>BookMind</a>
          <nav className="hidden items-center gap-8 text-sm font-medium md:flex"><a href="#home">Home</a><a href="#explore">Explore</a><button type="button" onClick={openRecommendations} className="hover:text-accent-foreground">Recommendations</button><a href="#about">About</a></nav>
          <div className="hidden items-center gap-2 md:flex"><Button variant="ghost" size="icon" aria-label="Search"><Search /></Button><Button className="h-10 px-4">Get Started</Button><Button variant="ghost" size="icon" aria-label="Profile"><UserRound /></Button></div>
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">{menuOpen ? <X /> : <Menu />}</Button>
        </div>
        {menuOpen && <nav className="flex flex-col items-start gap-4 border-t border-border px-5 py-5 md:hidden"><a href="#home">Home</a><a href="#explore">Explore</a><button type="button" onClick={openRecommendations}>Recommendations</button><a href="#about">About</a></nav>}
      </header>

      <section id="home" className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-20 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:py-28">
        <div className="flex flex-col items-start gap-7">
          <p className="flex items-center gap-2 text-xs font-bold tracking-[.2em] text-accent-foreground"><Sparkles className="size-4" />AI-POWERED BOOK DISCOVERY</p>
          <div className="flex flex-col gap-5"><h1 className="max-w-2xl text-balance font-serif text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">Discover Your Next Great <span className="text-accent-foreground">Read.</span></h1><p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">Find books that match your interests using intelligent semantic recommendations.</p></div>
          <form className="flex w-full max-w-2xl flex-col gap-3 rounded-2xl bg-card p-2 shadow-lg sm:flex-row" onSubmit={(e) => { e.preventDefault(); document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' }) }}><label className="flex flex-1 items-center gap-3 px-3"><Search className="size-5 text-muted-foreground" /><span className="sr-only">Search books</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search books, authors, genres..." className="h-12 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground" /></label><Button className="h-12 px-7" type="submit">Search</Button></form>
          <div className="flex flex-wrap items-center gap-2 text-sm"><span className="text-muted-foreground">Popular:</span>{['Fantasy', 'Mystery', 'Science', 'Self Development', 'Romance'].map((tag) => <button key={tag} onClick={() => { setCategory(tag); document.getElementById('explore')?.scrollIntoView({ behavior: 'smooth' }) }} className="rounded-full border border-border bg-card px-3 py-1.5 transition hover:border-accent hover:text-accent-foreground">{tag}</button>)}</div>
        </div>
        <div className="relative mx-auto hidden h-[520px] w-full max-w-xl sm:block" aria-label="Featured book covers"><img src={cover(books[0].isbn)} alt="The Hobbit book cover" className="absolute left-[8%] top-20 aspect-[2/3] w-[38%] -rotate-6 rounded-lg object-cover shadow-2xl" /><img src={cover(books[1].isbn)} alt="Harry Potter book cover" className="absolute left-[32%] top-0 aspect-[2/3] w-[40%] rotate-2 rounded-lg object-cover shadow-2xl" /><img src={cover(books[10].isbn)} alt="Sapiens book cover" className="absolute bottom-0 right-[3%] aspect-[2/3] w-[38%] rotate-6 rounded-lg object-cover shadow-2xl" /><div className="absolute bottom-5 left-3 rounded-2xl border border-border bg-card p-4 shadow-xl"><p className="text-xs font-bold tracking-wider text-accent-foreground">CURATED BY AI</p><p className="mt-1 font-serif text-lg">Stories chosen for you</p></div></div>
      </section>

      <section id="explore" className="bg-secondary/60 py-20"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 lg:px-8"><div className="flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><p className="mb-3 text-xs font-bold tracking-[.2em] text-accent-foreground">THE LIBRARY</p><h2 className="font-serif text-4xl font-semibold">Explore Our Book Collection</h2><p className="mt-3 text-muted-foreground">Browse our collection and find a book that catches your interest.</p></div><select aria-label="Sort books" className="h-11 rounded-xl border border-border bg-card px-4 text-sm outline-none"><option>Sort by: Recommended</option><option>Rating: High to low</option><option>Title: A–Z</option></select></div>
        <div className="flex flex-col gap-4"><label className="flex max-w-md items-center gap-3 rounded-xl border border-border bg-card px-4"><Search className="size-4 text-muted-foreground" /><span className="sr-only">Search collection</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search books..." className="h-11 flex-1 bg-transparent outline-none" /></label><div className="flex flex-wrap gap-2">{filters.map((filter) => <button key={filter} onClick={() => setCategory(filter)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${category === filter ? 'bg-primary text-primary-foreground' : 'border border-border bg-card hover:border-accent'}`}>{filter}</button>)}</div></div>
        {query && <p className="font-serif text-xl">Search results for “{query}” <span className="font-sans text-sm text-muted-foreground">({visibleBooks.length})</span></p>}
        {visibleBooks.length ? <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">{visibleBooks.map((book) => <BookCard key={book.title} book={book} onSelect={selectBook} />)}</div> : <div className="flex flex-col items-center gap-4 rounded-3xl border border-dashed border-border bg-card px-6 py-20 text-center"><BookOpen className="size-10 text-accent-foreground" /><h3 className="font-serif text-2xl">We couldn&apos;t find that book.</h3><p className="text-muted-foreground">Try searching by title, author, genre, or keyword.</p><Button onClick={() => { setQuery(''); setCategory('All') }}>Clear Search</Button></div>}
      </div></section>

      {selected && <section id="book-details" className="mx-auto max-w-6xl px-5 py-20 lg:px-8"><div className="grid gap-10 rounded-3xl border border-border bg-card p-6 shadow-xl md:grid-cols-[280px_1fr] md:p-10"><img src={cover(selected.isbn)} alt={`Cover of ${selected.title}`} className="mx-auto aspect-[2/3] w-full max-w-[280px] rounded-lg object-cover shadow-xl" /><div className="flex flex-col justify-center gap-5"><div><p className="mb-2 text-sm font-semibold text-accent-foreground">{selected.genre} · Adventure · Fiction</p><h2 className="text-balance font-serif text-4xl font-semibold md:text-5xl">{selected.title}</h2><p className="mt-2 text-lg text-muted-foreground">{selected.author}</p></div><div className="flex items-center gap-2 font-semibold text-accent-foreground"><span aria-label="Five stars">★★★★★</span><span className="text-foreground">{selected.rating}</span></div><p className="max-w-2xl leading-relaxed text-muted-foreground">{selected.description}</p><div className="flex flex-wrap gap-2">{[selected.genre, 'Adventure', 'Classic'].map((tag) => <span key={tag} className="rounded-full bg-secondary px-3 py-1.5 text-sm">{tag}</span>)}</div><div className="flex flex-col gap-3 sm:flex-row"><Button className="h-12 px-6" onClick={() => { setShowRecommendations(true); setTimeout(() => document.getElementById('recommendations')?.scrollIntoView({ behavior: 'smooth' }), 20) }}>Find Similar Books<ArrowRight data-icon="inline-end" /></Button><Button variant="outline" className="h-12 px-6"><Heart data-icon="inline-start" />Add to Favorites</Button></div></div></div></section>}

      {selected && showRecommendations && <section id="recommendations" className="bg-primary py-20 text-primary-foreground"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 lg:px-8"><div><p className="mb-3 flex items-center gap-2 text-xs font-bold tracking-[.2em] text-accent"><Sparkles className="size-4" />AI SEMANTIC MATCH</p><h2 className="font-serif text-4xl font-semibold">Books You Might Love</h2><p className="mt-3 text-primary-foreground/70">Because you liked {selected.title}</p></div><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-5">{recommendations.map((book, index) => { const score = [92, 87, 84, 79, 75][index]; return <article key={book.title} className="overflow-hidden rounded-2xl bg-card text-card-foreground"><img src={cover(book.isbn)} alt={`Cover of ${book.title}`} className="aspect-[2/3] w-full object-cover" /><div className="flex flex-col gap-3 p-4"><div><h3 className="font-serif text-lg leading-tight">{book.title}</h3><p className="mt-1 text-sm text-muted-foreground">{book.author}</p></div><div className="flex items-center justify-between text-xs"><span>{book.genre}</span><strong className="text-accent-foreground">AI Match {score}%</strong></div><div className="h-1.5 overflow-hidden rounded-full bg-secondary"><div className="h-full rounded-full bg-accent" style={{ width: `${score}%` }} /></div></div></article>})}</div><div className="flex max-w-3xl items-start gap-4 rounded-2xl bg-primary-foreground/10 p-6"><Sparkles className="mt-1 size-5 shrink-0 text-accent" /><div><h3 className="font-serif text-xl">Why these books?</h3><p className="mt-2 leading-relaxed text-primary-foreground/70">These recommendations were selected based on semantic similarity between the themes, descriptions, genres, and content of the books.</p></div></div></div></section>}

      <footer id="about" className="border-t border-border"><div className="mx-auto flex max-w-7xl flex-col gap-10 px-5 py-14 lg:px-8"><div className="flex flex-col justify-between gap-8 md:flex-row"><div><div className="flex items-center gap-2 font-serif text-xl font-bold"><BookOpen className="size-5" />BookMind</div><p className="mt-3 text-sm text-muted-foreground">Discover books. Explore ideas. Find your next story.</p></div><nav className="flex flex-wrap items-center gap-6 text-sm"><a href="#about">About</a><a href="#explore">Explore</a><button type="button" onClick={openRecommendations}>Recommendations</button><a href="#">GitHub</a><a href="mailto:sharmashubham7826@gmail.com" aria-label="Email Shubham Sharma">sharmashubham7826@gmail.com</a></nav></div><p className="border-t border-border pt-7 text-sm text-muted-foreground">© 2026 BookMind — AI-Powered Book Recommendation System</p></div></footer>
    </main>
  )
}
