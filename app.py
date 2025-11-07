from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Import models and initialize db
from models import db, Book, User, Rating
db.init_app(app)

from recommendation_engine import HybridRecommender

# Initialize recommendation engine (will be trained after DB init)
recommender = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books"""
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'description': book.description,
        'year': book.year,
        'rating': book.average_rating
    } for book in books])

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book"""
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'description': book.description,
        'year': book.year,
        'rating': book.average_rating
    })

@app.route('/api/users/<int:user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    global recommender
    user = User.query.get_or_404(user_id)
    
    # Initialize recommender if not already done
    if recommender is None:
        recommender = HybridRecommender()
        recommender.train()
    
    # Get hybrid recommendations
    recommendations = recommender.get_hybrid_recommendations(user_id, n_recommendations=10)
    
    return jsonify({
        'user_id': user_id,
        'recommendations': recommendations
    })

@app.route('/api/users/<int:user_id>/rate', methods=['POST'])
def rate_book(user_id):
    """Rate a book"""
    global recommender
    data = request.json
    book_id = data.get('book_id')
    rating_value = data.get('rating')
    
    if not book_id or not rating_value:
        return jsonify({'error': 'book_id and rating are required'}), 400
    
    # Validate rating is between 1-5
    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'rating must be between 1 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'rating must be a valid integer'}), 400
    
    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    
    # Check if rating already exists
    existing_rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        rating = Rating(user_id=user_id, book_id=book_id, rating=rating_value)
        db.session.add(rating)
    
    db.session.commit()
    
    # Update book's average rating
    book.update_average_rating()
    
    # Note: Recommender retraining is deferred for performance.
    # In production, consider batch retraining or incremental updates.
    # For now, recommendations will be stale until next app restart.
    
    return jsonify({'message': 'Rating saved successfully'})

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username
    } for user in users])

@app.route('/api/similar/<int:book_id>', methods=['GET'])
def get_similar_books(book_id):
    """Get books similar to a given book"""
    global recommender
    book = Book.query.get_or_404(book_id)
    
    # Initialize recommender if not already done
    if recommender is None:
        recommender = HybridRecommender()
        recommender.train()
    
    similar_books = recommender.get_similar_books(book_id, n_recommendations=5)
    
    return jsonify({
        'book_id': book_id,
        'similar_books': similar_books
    })

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Book.query.count() > 0:
            print("Database already initialized")
            return
        
        # Add sample users
        users = [
            User(username='Alice'),
            User(username='Bob'),
            User(username='Charlie'),
            User(username='Diana'),
            User(username='Eve')
        ]
        for user in users:
            db.session.add(user)
        
        # Add sample books
        books = [
            Book(title='The Great Gatsby', author='F. Scott Fitzgerald', genre='Classic', 
                 description='A story of decadence and excess in 1920s America', year=1925),
            Book(title='To Kill a Mockingbird', author='Harper Lee', genre='Classic',
                 description='A gripping tale of racial inequality and childhood innocence', year=1960),
            Book(title='1984', author='George Orwell', genre='Science Fiction',
                 description='A dystopian social science fiction novel', year=1949),
            Book(title='Pride and Prejudice', author='Jane Austen', genre='Romance',
                 description='A romantic novel of manners', year=1813),
            Book(title='The Hobbit', author='J.R.R. Tolkien', genre='Fantasy',
                 description='A fantasy novel about the adventures of Bilbo Baggins', year=1937),
            Book(title='Harry Potter and the Sorcerer\'s Stone', author='J.K. Rowling', genre='Fantasy',
                 description='A young wizard discovers his magical heritage', year=1997),
            Book(title='The Catcher in the Rye', author='J.D. Salinger', genre='Classic',
                 description='A story of teenage rebellion and alienation', year=1951),
            Book(title='Lord of the Flies', author='William Golding', genre='Classic',
                 description='A group of boys stranded on an island descend into savagery', year=1954),
            Book(title='Brave New World', author='Aldous Huxley', genre='Science Fiction',
                 description='A dystopian novel set in a futuristic World State', year=1932),
            Book(title='The Lord of the Rings', author='J.R.R. Tolkien', genre='Fantasy',
                 description='An epic high-fantasy novel', year=1954),
            Book(title='Animal Farm', author='George Orwell', genre='Classic',
                 description='An allegorical novella about Soviet totalitarianism', year=1945),
            Book(title='Jane Eyre', author='Charlotte Brontë', genre='Romance',
                 description='A novel about the experiences of its eponymous heroine', year=1847),
            Book(title='Wuthering Heights', author='Emily Brontë', genre='Romance',
                 description='A story of passion and revenge', year=1847),
            Book(title='The Hunger Games', author='Suzanne Collins', genre='Science Fiction',
                 description='A dystopian novel about survival and rebellion', year=2008),
            Book(title='Fahrenheit 451', author='Ray Bradbury', genre='Science Fiction',
                 description='A dystopian novel about a future where books are banned', year=1953)
        ]
        for book in books:
            db.session.add(book)
        
        db.session.commit()
        
        # Add sample ratings
        import random
        for user in users:
            # Each user rates 5-10 random books
            num_ratings = random.randint(5, 10)
            rated_books = random.sample(books, num_ratings)
            for book in rated_books:
                rating_value = random.randint(3, 5)
                rating = Rating(user_id=user.id, book_id=book.id, rating=rating_value)
                db.session.add(rating)
        
        db.session.commit()
        
        # Update average ratings
        for book in books:
            book.update_average_rating()
        
        print("Database initialized with sample data")
        
        # Train the recommender
        global recommender
        recommender = HybridRecommender()
        recommender.train()
        print("Recommendation engine trained")

if __name__ == '__main__':
    init_db()
    # Use debug mode only in development, never in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
