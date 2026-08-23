const API_URL = "http://localhost:8000";
const ADMIN_USER = "admin";
const ADMIN_PASS = "admin123";

let allBooks = [];

function adminLogin() {
  const user = document.getElementById("adminUser").value;
  const pass = document.getElementById("adminPass").value;

  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    sessionStorage.setItem("adminLoggedIn", "true");
    document.getElementById("loginScreen").classList.add("hidden");
    document.getElementById("adminDashboard").classList.remove("hidden");
    loadBooks();
  } else {
    document.getElementById("loginError").classList.remove("hidden");
  }
}

function adminLogout() {
  sessionStorage.removeItem("adminLoggedIn");
  document.getElementById("loginScreen").classList.remove("hidden");
  document.getElementById("adminDashboard").classList.add("hidden");
}

async function addBook(e) {
  e.preventDefault();
  const btn = document.getElementById("addBtn");
  const status = document.getElementById("addStatus");
  btn.textContent = "Adding...";
  btn.disabled = true;

  const book = {
    isbn13: parseInt(document.getElementById("isbn13").value) || null,
    title: document.getElementById("title").value,
    authors: document.getElementById("authors").value,
    description: document.getElementById("description").value,
    thumbnail: document.getElementById("thumbnail").value,
    simple_categories: document.getElementById("category").value,
    joy: parseFloat(document.getElementById("joy").value) || 0,
    surprise: parseFloat(document.getElementById("surprise").value) || 0,
    anger: parseFloat(document.getElementById("anger").value) || 0,
    fear: parseFloat(document.getElementById("fear").value) || 0,
    sadness: parseFloat(document.getElementById("sadness").value) || 0,
  };

  try {
    const res = await fetch(`${API_URL}/admin/books`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(book),
    });

    if (!res.ok) throw new Error("Failed to add book");

    showStatus("addStatus", "✅ Book added successfully!", "success");
    document.getElementById("addBookForm").reset();
    loadBooks();
  } catch (e) {
    showStatus("addStatus", "❌ " + e.message, "error");
  } finally {
    btn.textContent = "Add Book";
    btn.disabled = false;
  }
}

async function loadBooks() {
  const tbody = document.getElementById("booksTableBody");
  tbody.innerHTML = `<tr><td colspan="5" class="loading-row">Loading books...</td></tr>`;

  try {
    const res = await fetch(`${API_URL}/admin/books`);
    const data = await res.json();
    allBooks = data.books;
    renderTable(allBooks);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="loading-row">❌ Failed to load books. Is the backend running?</td></tr>`;
  }
}

function renderTable(books) {
  const tbody = document.getElementById("booksTableBody");

  if (books.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="loading-row">No books found.</td></tr>`;
    return;
  }

  tbody.innerHTML = books.map(book => `
    <tr>
      <td><img src="${book.thumbnail || 'https://via.placeholder.com/40x55?text=N/A'}" alt="${book.title}" onerror="this.src='https://via.placeholder.com/40x55?text=N/A'" /></td>
      <td>${book.title}</td>
      <td>${book.authors}</td>
      <td>${book.simple_categories || '-'}</td>
      <td>
        <button class="edit-btn" onclick="openEdit(${book.id})">✏️ Edit</button>
        <button class="delete-btn" onclick="deleteBook(${book.id})">🗑️ Delete</button>
      </td>
    </tr>
  `).join("");
}

function filterBooks() {
  const query = document.getElementById("searchBooks").value.toLowerCase();
  const filtered = allBooks.filter(b =>
    b.title.toLowerCase().includes(query) ||
    b.authors.toLowerCase().includes(query)
  );
  renderTable(filtered);
}

function openEdit(id) {
  const book = allBooks.find(b => b.id === id);
  if (!book) return;

  document.getElementById("editId").value = book.id;
  document.getElementById("editTitle").value = book.title;
  document.getElementById("editAuthors").value = book.authors;
  document.getElementById("editCategory").value = book.simple_categories || "";
  document.getElementById("editThumbnail").value = book.thumbnail || "";
  document.getElementById("editDescription").value = book.description || "";

  document.getElementById("editModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("editModal").classList.add("hidden");
}

async function saveEdit() {
  const id = document.getElementById("editId").value;
  const updated = {
    title: document.getElementById("editTitle").value,
    authors: document.getElementById("editAuthors").value,
    simple_categories: document.getElementById("editCategory").value,
    thumbnail: document.getElementById("editThumbnail").value,
    description: document.getElementById("editDescription").value,
  };

  try {
    const res = await fetch(`${API_URL}/admin/books/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });

    if (!res.ok) throw new Error("Failed to update book");

    showStatus("editStatus", "✅ Book updated!", "success");
    loadBooks();
    setTimeout(closeModal, 1000);
  } catch (e) {
    showStatus("editStatus", "❌ " + e.message, "error");
  }
}

async function deleteBook(id) {
  if (!confirm("Are you sure you want to delete this book?")) return;

  try {
    const res = await fetch(`${API_URL}/admin/books/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete");
    loadBooks();
  } catch (e) {
    alert("❌ Failed to delete book");
  }
}

function showStatus(id, msg, type) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `status-msg ${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3000);
}

// Check login on page load
window.addEventListener("DOMContentLoaded", () => {
  if (sessionStorage.getItem("adminLoggedIn") === "true") {
    document.getElementById("loginScreen").classList.add("hidden");
    document.getElementById("adminDashboard").classList.remove("hidden");
    loadBooks();
  }

  document.getElementById("adminPass").addEventListener("keydown", e => {
    if (e.key === "Enter") adminLogin();
  });
});
