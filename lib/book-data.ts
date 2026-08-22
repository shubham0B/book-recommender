export type Book = {
  title: string
  author: string
  genre: string
  rating: number
  isbn: string
  description: string
  thumbnail?: string
}

export const books: Book[] = [
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

export function getFallbackCover(title: string = 'Book Title', author: string = 'Author', genre: string = 'Fiction'): string {
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
    <rect width="400" height="600" fill="url(#bg)" rx="10" />
    <rect width="46" height="600" fill="url(#spine)" />
    <rect x="22" y="22" width="356" height="556" fill="none" stroke="url(#gold)" stroke-width="1.8" stroke-opacity="0.7" rx="6" />
    <rect x="28" y="28" width="344" height="544" fill="none" stroke="url(#gold)" stroke-width="0.8" stroke-opacity="0.4" rx="4" />
    <rect x="120" y="55" width="160" height="24" rx="12" fill="#000" fill-opacity="0.4" stroke="url(#gold)" stroke-width="1" stroke-opacity="0.6"/>
    <text x="200" y="71" fill="#fbbf24" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="700" letter-spacing="2.5" text-anchor="middle">${escapeXml(cleanGenre)}</text>
    ${titleSvgLines}
    <text x="200" y="${authorY}" text-anchor="middle" fill="#e2e8f0" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="600" letter-spacing="1.5" filter="url(#shadow)">
      ${escapeXml(cleanAuthor.toUpperCase())}
    </text>
  </svg>`;

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

export const cover = (isbn?: string, thumbnail?: string, title?: string, author?: string, genre?: string) => {
  if (thumbnail && thumbnail !== 'cover-not-found.jpg' && thumbnail !== '/placeholder.svg' && !thumbnail.includes('placeholder.svg') && thumbnail.trim().length > 5 && thumbnail.startsWith('http')) {
    return thumbnail;
  }
  const cleanIsbn = (isbn || '').replace(/[^0-9X]/gi, '').trim();
  if (cleanIsbn.length >= 9 && cleanIsbn !== '0') {
    return `https://books.google.com/books/content?vid=ISBN${cleanIsbn}&printsec=frontcover&img=1&zoom=1`;
  }
  return '';
}

export const filters = [
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
