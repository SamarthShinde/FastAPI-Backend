```markdown
# FastAPI Backend – Hosted on Railway

## Overview
This **FastAPI-based backend** provides multiple authentication flows (traditional email/password, email-based OTP verification, Google Sign-In) and supports model inference/chatbot capabilities. It integrates various **LLM models** (e.g., Llama 3.2, Llama3.3, DeepSeek 70B, Phi-4) via **LangChain** tools for agent-based interactions.  
Deployed on **Railway**, it ensures seamless deployment, authentication, and inference features.

---

## Features

1. **Multi-Modal Authentication**  
   - **Traditional** (Register/Login) with email & password.  
   - **Email OTP Flow** for secure verification and password setup.  
   - **Google Sign-In** (ID token verification) for quick user onboarding.

2. **Chatbot & Model Inference**  
   - Supports multiple LLM models.  
   - **Agent-based Querying** using LangChain (e.g., Wikipedia, web search, math solver).

3. **Database Integration**  
   - Stores chat history and user data securely.  
   - Uses **SQLAlchemy** with SQLite or PostgreSQL.

4. **Secure Endpoints**  
   - **JWT-based** security for protected endpoints.  
   - Email-based OTP for additional verification steps.

5. **Railway Deployment**  
   - Environment-based configuration.  
   - Scalable hosting with minimal downtime.

---

## Technologies Used

- **FastAPI** – Python-based web framework  
- **OAuth2 + JWT** – Secure user authentication  
- **LangChain** – Agent-based interactions with LLMs  
- **SQLAlchemy** – ORM for database management  
- **Railway** – Deployment platform  
- **SMTP** – Email sending for OTP-based verification

---

## Setup & Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/SamarthShinde/FastAPI-Backend.git
   cd FastAPI-Backend
   ```

2. **Create & Activate a Virtual Environment (optional but recommended)**  
   ```bash
   conda create --name fastapi-backend python=3.10 -y
   conda activate fastapi-backend
   ```
   *(Or use `python3 -m venv venv`, etc.)*

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**  
   Create a `.env` file (or set variables in Railway dashboard):

   ```plaintext
   DATABASE_URL=postgresql://username:password@host:port/dbname
   SECRET_KEY=supersecretkey
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   GOOGLE_CLIENT_ID=306823103408-d41bf64qp50qvup16hpdm4h110i4r23f.apps.googleusercontent.com

   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SENDER_EMAIL=your_email@gmail.com
   ```

5. **Run the FastAPI Server Locally**  
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Access the Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Railway Deployment

Deployed on Railway at:  
[https://fastapi-backend-production-5677.up.railway.app](https://fastapi-backend-production-5677.up.railway.app)

Configure environment variables in the Railway dashboard, and your service will be accessible at this URL.

---

## Authentication & Endpoints

### A. Traditional Email/Password

1. **Register User**  
   - **Endpoint**: `POST /auth/register`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/register" \
          -H "Content-Type: application/json" \
          -d '{
               "username": "Alice",
               "email": "alice@example.com",
               "password": "secret123"
             }'
     ```

2. **Login User**  
   - **Endpoint**: `POST /auth/login`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/login" \
          -H "Content-Type: application/json" \
          -d '{
               "email": "alice@example.com",
               "password": "secret123"
             }'
     ```
   - **Response (example)**:
     ```json
     {
       "access_token": "your_jwt_token_here",
       "token_type": "bearer"
     }
     ```

### B. Email-Based Registration with OTP

1. **Initiate Email Registration**  
   - **Endpoint**: `POST /auth/email-register`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/email-register" \
          -H "Content-Type: application/json" \
          -d '{
               "email": "bob@gmail.com",
               "username": "Bob"
             }'
     ```

2. **Complete Email Registration**  
   - **Endpoint**: `POST /auth/email-register-complete`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/email-register-complete" \
          -H "Content-Type: application/json" \
          -d '{
               "email": "bob@gmail.com",
               "otp": "123456",
               "password": "secret123",
               "confirm_password": "secret123"
             }'
     ```

### C. Google Sign-In

1. **Google Login / Register**  
   - **Endpoint**: `POST /auth/google`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/google" \
          -H "Content-Type: application/json" \
          -d '{
               "id_token": "your_valid_google_id_token"
             }'
     ```

---

## Chat & Models

1. **Chat API**  
   - **Endpoint**: `POST /chat`  
   - **Sample**:
     ```bash
     curl -X POST "https://fastapi-backend-production-5677.up.railway.app/chat" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer your_jwt_token" \
          -d '{
               "model_name": "deepseek-r1:70b",
               "message": "Hello, how can you assist me?"
             }'
     ```

2. **Get Chat History**  
   - **Endpoint**: `GET /chat/history`  
   - **Sample**:
     ```bash
     curl -X GET "https://fastapi-backend-production-5677.up.railway.app/chat/history" \
          -H "Authorization: Bearer your_jwt_token"
     ```

3. **List Models**  
   - **Endpoint**: `GET /models`  
   - **Sample**:
     ```bash
     curl -X GET "https://fastapi-backend-production-5677.up.railway.app/models"
     ```

---

## Notes

- **JWT**: Use `Authorization: Bearer <jwt>` for all protected endpoints.
- **OTP Emails**: Check your SMTP config in `.env`.
- **Google ID Token**: Obtain valid tokens from client-side sign-in (e.g., `google_sign_in` in Flutter).

---

## Future Enhancements

- WebSocket support for real-time chat.
- Advanced Logging and error handling.
- OAuth2 scopes for more granular permissions.
- Frontend integration with a polished UI (e.g., Flutter or React).

---

## Usage & Commands

1. **Local Run**  
   ```bash
   uvicorn main:app --reload
   ```

2. **Railway Deployment**  
   - Push commits to GitHub.
   - Railway auto-deploys, reading environment variables from the dashboard.

3. **Testing**  
   - Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
   - cURL: Use sample commands above.

---

## Contact & Support

- **Email**: samarth.shinde505@gmail.com  
- **GitHub**: [SamarthShinde](https://github.com/SamarthShinde)  

For issues or feature requests, open a GitHub issue or contact me directly.

---

## Changelog

**2025-02-21**  
- Added email-based OTP verification for registration.  
- Integrated Google sign-in endpoint.  
- Updated chat endpoints for multiple LLM models.  
- Deployed stable version on Railway with environment-based config.
