# FastAPI Backend for LLM Chat Application

A robust FastAPI backend for a chat application that integrates with various LLM models.

## 🚀 Features

- **Database Support**: 
  - SQLite for local development
  - MySQL/PostgreSQL for production
  - Automatic database initialization
  - Connection pooling for production databases

- **Authentication**:
  - JWT-based authentication
  - Google OAuth integration
  - Secure password hashing

- **Chat Functionality**:
  - Conversation management
  - Message history
  - Multiple LLM model support
  - Response time tracking

- **User Management**:
  - User profiles
  - Settings management
  - Subscription handling
  - Payment integration

## 📦 Project Structure

```
FastAPI-Backend/
├── backend/              # Main application code
│   ├── api.py           # API routes and endpoints
│   ├── auth.py          # Authentication logic
│   ├── chat_service.py  # Chat service implementation
│   ├── config.py        # Configuration management
│   ├── db_utils.py      # Database utilities
│   └── .env             # Environment variables
├── DB/                  # Database related code
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   └── __init__.py      # Package initialization
├── data/                # SQLite database storage
├── model/               # LLM model integration
├── tests/               # Test files
│   └── test_db_connection.py
├── server.py            # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠 Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd FastAPI-Backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.local` to `backend/.env`
   - Update the variables as needed

5. **Run the application**:
   ```bash
   python server.py
   ```

## 🔧 Configuration

### Database Configuration

The application supports both SQLite and MySQL/PostgreSQL:

1. **SQLite (Default for local development)**:
   ```env
   DB_TYPE=sqlite
   DATABASE_URL=sqlite:///data/app.db
   ```

2. **MySQL/PostgreSQL**:
   ```env
   DB_TYPE=mysql  # or postgresql
   DATABASE_URL=mysql+pymysql://user:password@host:port/database
   ```

### Other Configuration

- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `OLLAMA_REMOTE_URL`: URL for Ollama API
- Email and payment configurations

## 🧪 Testing

Run the database tests:
```bash
python -m tests.test_db_connection
```

## 📝 API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 Recent Changes

- Switched to SQLite for local development
- Improved database connection handling
- Added connection pooling for production databases
- Reorganized project structure
- Added comprehensive testing
- Updated documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Samarth Shinde
- GitHub: [SamarthShinde](https://github.com/SamarthShinde)
- Email: samarth.shinde505@gmail.com
