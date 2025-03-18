# Ollama Chat Application

A full-stack chat application that uses Ollama for AI-powered conversations. The application features user authentication, chat history management, and support for multiple AI models.

## Features

- User authentication with email OTP verification
- Real-time chat with AI models
- Conversation history management
- Multiple AI model support
- User settings and preferences
- Responsive web interface

## Tech Stack

- Backend: FastAPI (Python)
- Database: SQLite
- AI: Ollama
- Authentication: JWT + Email OTP

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

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
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

1. Start the Ollama service:
```bash
ollama serve
```

2. Start the server:
```bash
python server.py
```

3. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register`: Register a new user
- `POST /auth/login`: Login with email and password
- `POST /auth/verify-otp`: Verify email OTP
- `POST /auth/forgot-password`: Request password reset
- `POST /auth/reset-password`: Reset password with OTP

### Chat
- `POST /chat`: Send a message to the AI
- `GET /conversations/current/messages`: Get current conversation history
- `GET /conversations`: List all conversations
- `POST /conversations`: Create a new conversation
- `DELETE /conversations/{conversation_id}`: Delete a conversation

### User Settings
- `GET /users/me/settings`: Get user settings
- `PUT /users/me/settings`: Update user settings

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