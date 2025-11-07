# Book Recommendation System / ระบบแนะนำหนังสือ

A web application for book recommendations with a hybrid recommendation engine that combines collaborative filtering and content-based filtering.

เว็บแอปพลิเคชันสำหรับแนะนำหนังสือด้วยระบบ hybrid recommendation ที่ผสมผสานระหว่าง collaborative filtering และ content-based filtering

## Features / คุณสมบัติ

- **Hybrid Recommendation System** - Combines collaborative and content-based filtering
  - ระบบ hybrid recommendation ที่ผสมผสาน collaborative filtering และ content-based filtering
- **Collaborative Filtering** - Recommendations based on similar users' preferences
  - แนะนำตามความชอบของผู้ใช้ที่มีความคล้ายคลึงกัน
- **Content-Based Filtering** - Recommendations based on book features (genre, author, description)
  - แนะนำตามคุณลักษณะของหนังสือ (แนว, ผู้เขียน, คำอธิบาย)
- **Similar Books** - Find books similar to ones you like
  - ค้นหาหนังสือที่คล้ายกับหนังสือที่คุณชอบ
- **Interactive Web Interface** - Browse books and get personalized recommendations
  - อินเทอร์เฟซเว็บแบบอินเทอร์แอกทีฟสำหรับเรียกดูหนังสือและรับคำแนะนำที่เป็นส่วนตัว

## Technology Stack / เทคโนโลยีที่ใช้

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: scikit-learn for similarity calculations
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Recommendation Engine**: Hybrid system combining:
  - User-based collaborative filtering with cosine similarity
  - Content-based filtering using TF-IDF vectorization

## Installation / การติดตั้ง

### Prerequisites / สิ่งที่ต้องมี

- Python 3.8 or higher

### Setup Steps / ขั้นตอนการติดตั้ง

1. Clone the repository:
```bash
git clone https://github.com/PaT1Wat/we.git
cd we
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
# Development mode (with debug features)
FLASK_ENV=development python app.py

# Production mode (recommended)
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

**Security Note**: Never run the application with `FLASK_ENV=development` in production environments. Debug mode should only be used during local development.

## Usage / การใช้งาน

1. **Select a User** - Choose a user from the dropdown menu
   - เลือกผู้ใช้จากเมนูแบบเลื่อนลง

2. **Get Recommendations** - Click the "Get Recommendations" button to see personalized book suggestions
   - คลิกปุ่ม "Get Recommendations" เพื่อดูคำแนะนำหนังสือที่เป็นส่วนตัว

3. **Browse All Books** - Scroll down to see all available books
   - เลื่อนลงเพื่อดูหนังสือทั้งหมดที่มี

4. **View Book Details** - Click on any book to see detailed information and similar books
   - คลิกที่หนังสือใด ๆ เพื่อดูข้อมูลโดยละเอียดและหนังสือที่คล้ายกัน

## How the Hybrid Recommendation System Works / ระบบ Hybrid Recommendation ทำงานอย่างไร

### 1. Collaborative Filtering
- Builds a user-item rating matrix
- Calculates user similarity using cosine similarity
- Predicts ratings for unrated books based on similar users' ratings
- สร้างเมทริกซ์การให้คะแนนผู้ใช้-รายการ
- คำนวณความคล้ายคลึงของผู้ใช้โดยใช้ cosine similarity
- ทำนายคะแนนสำหรับหนังสือที่ยังไม่ได้ให้คะแนนตามคะแนนของผู้ใช้ที่คล้ายกัน

### 2. Content-Based Filtering
- Extracts features from books (genre, author, description)
- Uses TF-IDF vectorization to create feature vectors
- Calculates book similarity using cosine similarity
- Recommends books similar to those the user has rated highly
- ดึงคุณลักษณะจากหนังสือ (แนว, ผู้เขียน, คำอธิบาย)
- ใช้ TF-IDF vectorization เพื่อสร้างเวกเตอร์คุณลักษณะ
- คำนวณความคล้ายคลึงของหนังสือโดยใช้ cosine similarity
- แนะนำหนังสือที่คล้ายกับหนังสือที่ผู้ใช้ให้คะแนนสูง

### 3. Hybrid Approach
- Combines both methods with weighted scoring (default: 50% collaborative, 50% content-based)
- Provides more robust and diverse recommendations
- Handles cold-start problem better than individual methods
- ผสมผสานทั้งสองวิธีด้วยคะแนนถ่วงน้ำหนัก (ค่าเริ่มต้น: 50% collaborative, 50% content-based)
- ให้คำแนะนำที่แข็งแกร่งและหลากหลายมากขึ้น
- จัดการกับปัญหา cold-start ได้ดีกว่าวิธีการแต่ละแบบ

## API Endpoints

- `GET /api/books` - Get all books
- `GET /api/books/<id>` - Get a specific book
- `GET /api/users` - Get all users
- `GET /api/users/<id>/recommendations` - Get personalized recommendations
- `GET /api/similar/<book_id>` - Get similar books
- `POST /api/users/<id>/rate` - Rate a book

## Project Structure / โครงสร้างโปรเจค

```
we/
├── app.py                      # Main Flask application
├── models.py                   # Database models (Book, User, Rating)
├── recommendation_engine.py    # Hybrid recommendation system
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Main web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend JavaScript
└── README.md                   # This file
```

## Sample Data / ข้อมูลตัวอย่าง

The application comes with sample data including:
- 15 classic and popular books across different genres
- 5 sample users with random ratings
- Pre-trained recommendation models

แอปพลิเคชันมาพร้อมกับข้อมูลตัวอย่างรวมถึง:
- หนังสือคลาสสิกและยอดนิยม 15 เล่มในหลายแนว
- ผู้ใช้ตัวอย่าง 5 คนพร้อมคะแนนแบบสุ่ม
- โมเดลคำแนะนำที่ผ่านการฝึกอบรมแล้ว

## Future Enhancements / การพัฒนาในอนาคต

- User authentication and registration
- Book search and filtering
- User rating interface
- More sophisticated recommendation algorithms
- Book cover images
- Reviews and comments system

## License

MIT License