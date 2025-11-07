from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Book(db.Model):
    """Book model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    year = db.Column(db.Integer)
    average_rating = db.Column(db.Float, default=0.0)
    
    ratings = db.relationship('Rating', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def update_average_rating(self):
        """Update the average rating for this book"""
        if self.ratings:
            total = sum(r.rating for r in self.ratings)
            self.average_rating = total / len(self.ratings)
        else:
            self.average_rating = 0.0
        db.session.commit()
    
    def __repr__(self):
        return f'<Book {self.title}>'

class User(db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Rating(db.Model):
    """Rating model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),)
    
    def __repr__(self):
        return f'<Rating user={self.user_id} book={self.book_id} rating={self.rating}>'
