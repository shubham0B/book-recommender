export type Book = {
  title: string
  author: string
  genre: string
  rating: number
  isbn: string
  description: string
}

export const books: Book[] = [
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

export const cover = (isbn: string) => `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`
export const filters = ['All', 'Fiction', 'Fantasy', 'Mystery', 'Romance', 'Science', 'Self Development', 'History']
