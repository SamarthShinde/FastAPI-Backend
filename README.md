# Ollama Chat Application

A full-stack chat application that uses Ollama for AI-powered conversations. The application features user authentication with OTP verification, chat history management, and support for multiple AI models.

## Features

- User authentication with email OTP verification
- Real-time chat with AI models
- Conversation history management
- Multiple AI model support
- User settings and preferences
- Dark/Light theme support

## Tech Stack

- Backend: FastAPI (Python)
- Database: SQLite
- AI: Ollama
- Authentication: JWT + Email OTP

## API Documentation

### Authentication

1. Register a new user (sends OTP):
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "your.email@example.com",
    "password": "your_password"
  }'
```

2. Verify OTP after registration:
```bash
curl -X POST http://localhost:8000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "otp": "123456"
  }'
```

3. Login with password:
```bash
curl -X POST http://localhost:8000/login/password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "your_password"
  }'
```

4. Request OTP for login:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com"
  }'
```

### Chat Operations

1. Send a message:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Hello, how are you?"
  }'
```

2. Get current conversation messages:
```bash
curl -X GET http://localhost:8000/conversations/current/messages \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. Get all conversations:
```bash
curl -X GET http://localhost:8000/conversations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. Create new conversation:
```bash
curl -X POST http://localhost:8000/conversations/new \
  -H "Authorization: Bearer YOUR_TOKEN"
```

5. Switch conversation:
```bash
curl -X POST http://localhost:8000/conversations/{conversation_id}/switch \
  -H "Authorization: Bearer YOUR_TOKEN"
```

6. Archive conversation:
```bash
curl -X DELETE http://localhost:8000/conversations/{conversation_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### User Settings

1. Get user settings:
```bash
curl -X GET http://localhost:8000/settings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. Update user settings:
```bash
curl -X PUT http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "theme": "dark",
    "preferred_model": "llama2",
    "language_preference": "English",
    "notifications_enabled": true
  }'
```

### User Profile

1. Get current user info:
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. Update user profile:
```bash
curl -X PUT http://localhost:8000/users/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "new_username",
    "email": "new.email@example.com"
  }'
```

### AI Models

1. Get available models:
```bash
curl -X GET http://localhost:8000/models/available \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. Update active model:
```bash
curl -X POST http://localhost:8000/models/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "model_name": "llama2"
  }'
```

## Project Structure

```
.
├── backend/                 # Backend API and services
│   ├── api.py              # Main FastAPI routes and endpoints
│   ├── api_dummy.py        # Dummy API routes for testing
│   ├── auth.py             # Authentication and authorization
│   ├── chat_service.py     # Chat functionality implementation
│   ├── config.py           # Application configuration
│   ├── db_utils.py         # Database utility functions
│   ├── email_utils.py      # Email utilities for notifications
│   ├── payment_utils.py    # Payment processing utilities
│   └── requirements.txt    # Backend dependencies
├── DB/                     # Database related files
│   ├── database.py         # Database connection setup
│   ├── delete_user.py      # User deletion utilities
│   ├── init_db.py          # Database initialization
│   ├── main.py             # Main database operations
│   └── models.py           # SQLAlchemy models
├── model/                  # AI model related code
│   ├── ai_agents.py        # AI agent implementation
│   ├── model_code.py       # Model interaction logic
│   └── __init__.py         # Package initialization
├── server.py               # Server startup script
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables
```

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SamarthShinde/FastAPI-Backend.git
cd FastAPI-Backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```
DATABASE_URL=sqlite:///./chat.db
SECRET_KEY=your-secret-key
OLLAMA_REMOTE_URL=http://localhost:11434/api/generate
```

5. Initialize the database:
```bash
python DB/init_db.py
```

## Running the Application

1. Start Ollama service:
```bash
ollama serve
```

2. Start the backend server:
```bash
python server.py
```

3. Start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Samarth Shinde
- GitHub: [SamarthShinde](https://github.com/SamarthShinde)
- Email: samarth.shinde505@gmail.com
