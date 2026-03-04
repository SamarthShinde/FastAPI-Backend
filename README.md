# Samarth LLM Chat — Backend

A full-stack AI chat application powered by [Ollama](https://ollama.com) local models, built with FastAPI + SQLite + Flutter + React.

---

## Project Structure

```
Samarth_LLM_Chat/
├── backend/                   # FastAPI server (this repo)
│   ├── server.py              # Entry point — run this to start
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini            # DB migration config
│   │
│   ├── api/                   # Routes, auth, services, config
│   │   ├── api.py             # All API endpoints (28 routes)
│   │   ├── auth.py            # JWT auth + OTP
│   │   ├── chat_service.py    # Chat logic
│   │   ├── config.py          # Loads .env settings
│   │   ├── db_utils.py        # DB query helpers
│   │   ├── email_utils.py     # SMTP email (OTP)
│   │   ├── payment_utils.py   # Razorpay integration
│   │   └── .env               # Environment variables (secrets)
│   │
│   ├── database/              # Database layer
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── database.py        # Engine, session, connection pooling
│   │   ├── base.py            # Declarative base
│   │   ├── init_db.py         # Creates tables on startup
│   │   ├── delete_user.py     # Utility: delete user by email
│   │   └── data/
│   │       └── app.db         # SQLite database file
│   │
│   ├── ollama/                # Local LLM integration
│   │   ├── model_code.py      # Streaming response generator
│   │   └── ai_agents.py       # ChatAgent class with context
│   │
│   ├── migrations/            # Alembic DB migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   ├── static/                # Basic HTML/CSS/JS web UI
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── script.js
│   │
│   └── tests/
│       └── test_db_connection.py
│
├── frontend/                  # React web app (Vite + TailwindCSS)
├── mobile/                    # Flutter mobile app (iOS + Android)
└── docs/                      # Project documentation
```

---

## Setup & Run

### Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed and running
- Conda or virtualenv

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment

Edit `api/.env`:

```env
DB_TYPE=sqlite
DATABASE_URL=sqlite:///database/data/app.db

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

OLLAMA_REMOTE_URL=http://localhost:11434/api/generate

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your@email.com
```

### 3. Start Ollama and pull a model

```bash
ollama serve
ollama pull qwen2.5:3b
```

### 4. Run the server

```bash
python server.py
```

Server starts on `http://localhost:8000`

---

## Available Models

| Model        | Size   | Notes   |
|--------------|--------|---------|
| `qwen2.5:3b` | 1.9 GB | Default |
| `llama3.2:3b`| 2.0 GB |         |
| `gemma3`     | varies |         |

---

## API Endpoints

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Auth

| Method | Endpoint      | Description          |
|--------|---------------|----------------------|
| POST   | `/register`   | Register new user    |
| POST   | `/login`      | Login, get JWT token |
| POST   | `/send-otp`   | Send OTP to email    |
| POST   | `/verify-otp` | Verify OTP           |

### Chat

| Method | Endpoint                         | Description          |
|--------|----------------------------------|----------------------|
| POST   | `/chat`                          | Send a message       |
| GET    | `/conversations`                 | List conversations   |
| GET    | `/conversations/{id}/messages`   | Get messages         |
| DELETE | `/conversations/{id}`            | Delete conversation  |

### Models

| Method | Endpoint            | Description           |
|--------|---------------------|-----------------------|
| GET    | `/models/available` | List available models |

---

## Example Usage

### Register

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret"}'
```

### Login

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret"}'
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b", "message": "Hello!"}'
```

---

## Database

SQLite by default — file at `database/data/app.db`

Tables: `Users`, `Conversations`, `Messages`, `User_Settings`, `Subscriptions`, `Payments`

Run migrations:

```bash
alembic upgrade head
```

Test DB connection:

```bash
python -m tests.test_db_connection
```

---

## Deployment

The backend is exposed via Cloudflare Tunnel at `https://www.ollama-app.thecit.in`

To restart the tunnel:

```bash
launchctl start com.cloudflare.cloudflared
```

---

## License

MIT License — see [LICENSE](LICENSE)

## Author

Samarth Shinde

- GitHub: [SamarthShinde](https://github.com/SamarthShinde)
- Email: samarth.shinde505@gmail.com
