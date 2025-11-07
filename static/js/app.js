// API base URL
const API_BASE = '/api';

// Global state
let currentUser = null;
let allBooks = [];
let users = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadAllBooks();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const userSelect = document.getElementById('user-select');
    const getRecsBtn = document.getElementById('get-recommendations');
    const modal = document.getElementById('book-modal');
    const closeBtn = document.querySelector('.close');

    userSelect.addEventListener('change', (e) => {
        currentUser = e.target.value;
        getRecsBtn.disabled = !currentUser;
    });

    getRecsBtn.addEventListener('click', () => {
        if (currentUser) {
            loadRecommendations(currentUser);
        }
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
}

// Load users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        users = await response.json();
        
        const userSelect = document.getElementById('user-select');
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.username;
            userSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

// Load all books
async function loadAllBooks() {
    try {
        const response = await fetch(`${API_BASE}/books`);
        allBooks = await response.json();
        displayBooks(allBooks, 'all-books');
    } catch (error) {
        console.error('Error loading books:', error);
        alert('Failed to load books');
    }
}

// Load recommendations for a user
async function loadRecommendations(userId) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/recommendations`);
        const data = await response.json();
        
        const recsSection = document.getElementById('recommendations-section');
        recsSection.classList.remove('hidden');
        
        displayBooks(data.recommendations, 'recommendations');
        
        // Scroll to recommendations
        recsSection.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error loading recommendations:', error);
        alert('Failed to load recommendations');
    }
}

// Display books in a grid
function displayBooks(books, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (books.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #666;">No books to display</p>';
        return;
    }

    books.forEach(book => {
        const bookCard = createBookCard(book);
        container.appendChild(bookCard);
    });
}

// Create a book card element
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    
    const rating = book.rating ? book.rating.toFixed(1) : 'N/A';
    const stars = book.rating ? '⭐'.repeat(Math.round(book.rating)) : '';
    
    card.innerHTML = `
        <h3>${escapeHtml(book.title)}</h3>
        <p class="author">by ${escapeHtml(book.author)}</p>
        <span class="genre">${escapeHtml(book.genre)}</span>
        <p class="rating">${stars} ${rating}/5</p>
        <p class="year">${book.year}</p>
    `;
    
    card.addEventListener('click', () => showBookDetails(book.id));
    
    return card;
}

// Show book details in modal
async function showBookDetails(bookId) {
    try {
        const [bookResponse, similarResponse] = await Promise.all([
            fetch(`${API_BASE}/books/${bookId}`),
            fetch(`${API_BASE}/similar/${bookId}`)
        ]);
        
        const book = await bookResponse.json();
        const similarData = await similarResponse.json();
        
        const modal = document.getElementById('book-modal');
        const detailsContainer = document.getElementById('book-details');
        
        const rating = book.rating ? book.rating.toFixed(1) : 'N/A';
        const stars = book.rating ? '⭐'.repeat(Math.round(book.rating)) : '';
        
        detailsContainer.innerHTML = `
            <h2>${escapeHtml(book.title)}</h2>
            <p><span class="detail-label">Author:</span> ${escapeHtml(book.author)}</p>
            <p><span class="detail-label">Genre:</span> ${escapeHtml(book.genre)}</p>
            <p><span class="detail-label">Year:</span> ${book.year}</p>
            <p><span class="detail-label">Rating:</span> ${stars} ${rating}/5</p>
            <p><span class="detail-label">Description:</span> ${escapeHtml(book.description || 'No description available')}</p>
        `;
        
        // Display similar books
        const similarSection = document.getElementById('similar-section');
        const similarContainer = document.getElementById('modal-similar-books');
        
        if (similarData.similar_books && similarData.similar_books.length > 0) {
            similarSection.classList.remove('hidden');
            similarContainer.innerHTML = '';
            
            similarData.similar_books.forEach(similar => {
                const item = document.createElement('div');
                item.className = 'book-list-item';
                
                const similarity = similar.similarity ? (similar.similarity * 100).toFixed(0) : 0;
                
                item.innerHTML = `
                    <h4>${escapeHtml(similar.title)}</h4>
                    <p>by ${escapeHtml(similar.author)} | ${escapeHtml(similar.genre)}</p>
                    <p class="similarity-score">Similarity: ${similarity}%</p>
                `;
                
                item.addEventListener('click', () => {
                    modal.classList.add('hidden');
                    setTimeout(() => showBookDetails(similar.id), 300);
                });
                
                similarContainer.appendChild(item);
            });
        } else {
            similarSection.classList.add('hidden');
        }
        
        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading book details:', error);
        alert('Failed to load book details');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    if (text == null) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
