const API_URL = "http://localhost:8000";

// Load categories on page load
async function loadCategories() {
  try {
    const res = await fetch(`${API_URL}/categories`);
    const data = await res.json();
    const select = document.getElementById("category");
    data.categories.forEach(cat => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error("Could not load categories:", e);
  }
}

async function searchBooks() {
  const query = document.getElementById("query").value.trim();
  const category = document.getElementById("category").value;
  const tone = document.getElementById("tone").value;

  if (!query) {
    showError("Please enter a description to search for books.");
    return;
  }

  showLoading(true);
  clearError();
  clearResults();

  try {
    const res = await fetch(`${API_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, category, tone }),
    });

    if (!res.ok) throw new Error("Server error. Please try again.");

    const data = await res.json();
    renderBooks(data.recommendations);
  } catch (e) {
    showError(e.message || "Something went wrong. Make sure the backend is running.");
  } finally {
    showLoading(false);
  }
}

function renderBooks(books) {
  const grid = document.getElementById("results");
  const title = document.getElementById("resultsTitle");

  if (!books || books.length === 0) {
    showError("No books found. Try a different search.");
    return;
  }

  title.classList.remove("hidden");

  books.forEach(book => {
    const card = document.createElement("div");
    card.className = "book-card";
    card.innerHTML = `
      <img src="${book.thumbnail}" alt="${book.title}" onerror="this.src='https://via.placeholder.com/160x220?text=No+Cover'" />
      <div class="book-info">
        <div class="book-title">${book.title}</div>
        <div class="book-author">${book.authors}</div>
        <div class="book-desc">${book.description}</div>
        <div class="book-links">
          <a href="${book.links.open_library}" target="_blank" title="Open Library">📖 Open Library</a>
          <a href="${book.links.gutenberg}" target="_blank" title="Project Gutenberg">📜 Gutenberg</a>
          <a href="${book.links.google_books}" target="_blank" title="Search free online">🔍 Find Free</a>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function showLoading(show) {
  document.getElementById("loading").classList.toggle("hidden", !show);
}

function showError(msg) {
  const el = document.getElementById("error");
  el.textContent = msg;
  el.classList.remove("hidden");
}

function clearError() {
  const el = document.getElementById("error");
  el.textContent = "";
  el.classList.add("hidden");
}

function clearResults() {
  document.getElementById("results").innerHTML = "";
  document.getElementById("resultsTitle").classList.add("hidden");
}

// Allow pressing Enter to search
document.addEventListener("DOMContentLoaded", () => {
  loadCategories();
  document.getElementById("query").addEventListener("keydown", e => {
    if (e.key === "Enter") searchBooks();
  });
});

async function analyzeCover() {
  const fileInput = document.getElementById("coverFile");
  const urlInput = document.getElementById("coverUrl").value.trim();
  const loading = document.getElementById("coverLoading");
  const errorEl = document.getElementById("coverError");
  const resultEl = document.getElementById("coverResult");

  errorEl.classList.add("hidden");
  resultEl.classList.add("hidden");
  loading.classList.remove("hidden");

  try {
    const formData = new FormData();
    if (fileInput.files.length > 0) {
      formData.append("file", fileInput.files[0]);
      document.getElementById("coverPreview").src = URL.createObjectURL(fileInput.files[0]);
    } else if (urlInput) {
      formData.append("image_url", urlInput);
      document.getElementById("coverPreview").src = urlInput;
    } else {
      throw new Error("Please upload an image or paste an image URL.");
    }

    const res = await fetch(`${API_URL}/summarize-cover`, { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await res.json();
    document.getElementById("coverTitle").textContent = data.title || "Unknown";
    document.getElementById("coverAuthor").textContent = data.author || "Unknown";
    document.getElementById("coverGenre").textContent = data.genre || "Unknown";
    document.getElementById("coverSummary").textContent = data.summary || "";
    resultEl.classList.remove("hidden");
  } catch (e) {
    errorEl.textContent = e.message;
    errorEl.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
  }
}
