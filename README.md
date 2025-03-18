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
- Frontend: React
- Database: SQLite
- AI: Ollama
- Authentication: JWT + Email OTP

## Prerequisites

- Python 3.8+
- Node.js 14+
- Ollama installed and running locally
- Git

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create a `.env` file in the backend directory with the following variables:
```
DATABASE_URL=sqlite:///./chat.db
SECRET_KEY=your-secret-key
OLLAMA_REMOTE_URL=http://localhost:11434/api/generate
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn api:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Make sure Ollama is running locally with the required models installed.

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.