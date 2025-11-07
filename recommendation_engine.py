import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class HybridRecommender:
    """
    Hybrid Recommendation System combining:
    1. Collaborative Filtering (User-based)
    2. Content-based Filtering (based on book features)
    """
    
    def __init__(self):
        self.user_similarity_matrix = None
        self.content_similarity_matrix = None
        self.user_book_matrix = None
        self.book_ids = []
        self.user_ids = []
        
    def train(self):
        """Train both collaborative and content-based models"""
        print("Training recommendation engine...")
        self._train_collaborative_filtering()
        self._train_content_based()
        print("Training complete!")
    
    def _train_collaborative_filtering(self):
        """Train collaborative filtering model using user-item matrix"""
        from models import Rating
        # Get all ratings
        ratings = Rating.query.all()
        if not ratings:
            print("No ratings found for training")
            return
        
        # Create user-book matrix
        rating_data = [{
            'user_id': r.user_id,
            'book_id': r.book_id,
            'rating': r.rating
        } for r in ratings]
        
        df = pd.DataFrame(rating_data)
        
        # Create pivot table (user-book matrix)
        self.user_book_matrix = df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        
        self.user_ids = self.user_book_matrix.index.tolist()
        self.book_ids = self.user_book_matrix.columns.tolist()
        
        # Calculate user similarity matrix using cosine similarity
        if len(self.user_ids) > 1:
            self.user_similarity_matrix = cosine_similarity(self.user_book_matrix)
        else:
            self.user_similarity_matrix = np.array([[1.0]])
        
        print(f"Collaborative filtering trained with {len(self.user_ids)} users and {len(self.book_ids)} books")
    
    def _train_content_based(self):
        """Train content-based model using book features"""
        from models import Book
        books = Book.query.all()
        if not books:
            print("No books found for training")
            return
        
        # Create feature vectors from book metadata
        book_features = []
        book_ids = []
        
        for book in books:
            # Combine text features
            features = f"{book.genre} {book.author} {book.description or ''}"
            book_features.append(features)
            book_ids.append(book.id)
        
        # Use TF-IDF to vectorize book features
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf_matrix = vectorizer.fit_transform(book_features)
        
        # Calculate book similarity matrix
        self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
        
        print(f"Content-based filtering trained with {len(books)} books")
    
    def _collaborative_recommendations(self, user_id, n_recommendations=10):
        """Get recommendations using collaborative filtering"""
        if self.user_similarity_matrix is None or user_id not in self.user_ids:
            return []
        
        # Get user index
        user_idx = self.user_ids.index(user_id)
        
        # Get similar users (excluding the user themselves)
        user_similarities = self.user_similarity_matrix[user_idx]
        similar_user_indices = np.argsort(user_similarities)[::-1][1:]  # Exclude self
        
        # Get books rated by similar users but not by target user
        user_ratings = self.user_book_matrix.loc[user_id]
        unrated_books = user_ratings[user_ratings == 0].index.tolist()
        
        # Calculate predicted ratings for unrated books
        book_scores = {}
        for book_id in unrated_books:
            if book_id not in self.book_ids:
                continue
            
            # Weighted average of ratings from similar users
            total_similarity = 0
            weighted_sum = 0
            
            for similar_user_idx in similar_user_indices[:10]:  # Top 10 similar users
                similar_user_id = self.user_ids[similar_user_idx]
                similarity = user_similarities[similar_user_idx]
                
                if similarity <= 0:
                    continue
                
                similar_user_rating = self.user_book_matrix.loc[similar_user_id, book_id]
                if similar_user_rating > 0:
                    weighted_sum += similarity * similar_user_rating
                    total_similarity += similarity
            
            if total_similarity > 0:
                book_scores[book_id] = weighted_sum / total_similarity
        
        # Sort by predicted rating
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
        return [book_id for book_id, score in sorted_books[:n_recommendations]]
    
    def _content_based_recommendations(self, user_id, n_recommendations=10):
        """Get recommendations using content-based filtering"""
        from models import Rating, Book
        if self.content_similarity_matrix is None:
            return []
        
        # Get books the user has rated highly (4 or 5 stars)
        user_ratings = Rating.query.filter_by(user_id=user_id).filter(Rating.rating >= 4).all()
        if not user_ratings:
            return []
        
        # Get all books
        all_books = Book.query.all()
        book_id_to_idx = {book.id: idx for idx, book in enumerate(all_books)}
        
        # Find similar books to highly rated books
        book_scores = {}
        rated_book_ids = {r.book_id for r in user_ratings}
        
        for rating in user_ratings:
            book_id = rating.book_id
            if book_id not in book_id_to_idx:
                continue
            
            book_idx = book_id_to_idx[book_id]
            similarities = self.content_similarity_matrix[book_idx]
            
            for idx, similarity in enumerate(similarities):
                candidate_book_id = all_books[idx].id
                
                # Skip if already rated
                if candidate_book_id in rated_book_ids:
                    continue
                
                # Accumulate similarity scores
                if candidate_book_id not in book_scores:
                    book_scores[candidate_book_id] = 0
                book_scores[candidate_book_id] += similarity * rating.rating
        
        # Sort by score
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
        return [book_id for book_id, score in sorted_books[:n_recommendations]]
    
    def get_hybrid_recommendations(self, user_id, n_recommendations=10, alpha=0.5):
        """
        Get hybrid recommendations combining collaborative and content-based
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            alpha: Weight for collaborative filtering (1-alpha for content-based)
        """
        # Get recommendations from both methods
        collab_recs = self._collaborative_recommendations(user_id, n_recommendations * 2)
        content_recs = self._content_based_recommendations(user_id, n_recommendations * 2)
        
        # Combine recommendations with weights
        book_scores = {}
        
        # Add collaborative filtering scores
        for idx, book_id in enumerate(collab_recs):
            score = alpha * (len(collab_recs) - idx) / len(collab_recs)
            book_scores[book_id] = book_scores.get(book_id, 0) + score
        
        # Add content-based scores
        for idx, book_id in enumerate(content_recs):
            score = (1 - alpha) * (len(content_recs) - idx) / len(content_recs)
            book_scores[book_id] = book_scores.get(book_id, 0) + score
        
        # Sort by combined score
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_book_ids = [book_id for book_id, score in sorted_books[:n_recommendations]]
        
        # Get book details
        from models import Book
        recommendations = []
        for book_id in recommended_book_ids:
            book = Book.query.get(book_id)
            if book:
                recommendations.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'genre': book.genre,
                    'description': book.description,
                    'year': book.year,
                    'rating': book.average_rating
                })
        
        return recommendations
    
    def get_similar_books(self, book_id, n_recommendations=5):
        """Get books similar to a given book using content-based similarity"""
        from models import Book
        if self.content_similarity_matrix is None:
            return []
        
        all_books = Book.query.all()
        book_id_to_idx = {book.id: idx for idx, book in enumerate(all_books)}
        
        if book_id not in book_id_to_idx:
            return []
        
        book_idx = book_id_to_idx[book_id]
        similarities = self.content_similarity_matrix[book_idx]
        
        # Get most similar books (excluding the book itself)
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            book = all_books[idx]
            recommendations.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'description': book.description,
                'year': book.year,
                'rating': book.average_rating,
                'similarity': float(similarities[idx])
            })
        
        return recommendations
