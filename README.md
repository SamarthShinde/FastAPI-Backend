Here’s the **updated README.md** for your GitHub repository, reflecting the latest changes and modifications:

---

# FastAPI Backend - Hosted on Railway

## 📌 Overview
This is a **FastAPI-based backend** that provides authentication, model inference, and chatbot capabilities. It supports multiple **LLM models (e.g., Llama 3.2, Llama3.3, DeepSeek 70B, Phi-4)** and integrates LangChain tools for intelligent agent-based interactions.

The backend is deployed on **Railway**, ensuring smooth deployment, authentication, and inference capabilities.

---

## 🚀 Features
- **User Authentication** (Register, Login, Logout) using JWT tokens.
- **Chatbot API** for model inference with support for multiple LLM models.
- **Agent-based Querying** using LangChain tools (e.g., Wikipedia, Web Search, Math Solver).
- **Database Integration** for chat history storage.
- **Secure API endpoints** with JWT authentication.
- **Railway Deployment** for cloud hosting.

---

## 🛠️ Technologies Used
- **FastAPI** (Backend Framework)
- **OAuth2 with JWT** (Authentication)
- **LangChain** (For AI agents and tool-based interactions)
- **Ollama API** (LLM Model Integration)
- **Railway** (Deployment Platform)
- **SQLite / PostgreSQL** (Database for storing chat history)

---

## 📌 Setup & Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/SamarthShinde/Audio_Classification.git
cd Audio_Classification
```

### **2️⃣ Set Up Virtual Environment (Optional but Recommended)**
```bash
conda create --name fastapi-backend python=3.10 -y
conda activate fastapi-backend
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Run the FastAPI Server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Your backend will be available at: **`http://127.0.0.1:8000`**

---

## 🌐 Railway Deployment
The backend is deployed on **Railway** at:
🔗 **`https://fastapi-backend-production-5677.up.railway.app`**

---

## 🔐 Authentication (JWT-based)
All protected endpoints require a **JWT Token** obtained after login.

---

## 📌 API Endpoints & Usage

### **1️⃣ Register a New User**
```bash
curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "------",
           "email": "-----",
           "password": "-----"
         }'
```

### **2️⃣ Login to Get JWT Token**
```bash
curl -X POST "https://fastapi-backend-production-5677.up.railway.app/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "-------",
           "password": "-------"
         }'
```
**Response:**
```json
{
  "access_token": "your_generated_jwt_token",
  "token_type": "bearer"
}
```

### **3️⃣ Use Model Inference API (Authenticated Request)**
```bash
curl -X POST "https://fastapi-backend-production-5677.up.railway.app/chat" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_generated_jwt_token" \
     -d '{
           "model_name": "deepseek-r1:70b",
           "message": "What can you do?"
         }'
```

### **4️⃣ Fetch Chat History (Authenticated Request)**
```bash
curl -X GET "https://fastapi-backend-production-5677.up.railway.app/chat/history" \
     -H "Authorization: Bearer your_generated_jwt_token"
```

### **5️⃣ List Available Models**
```bash
curl -X GET "https://fastapi-backend-production-5677.up.railway.app/models"
```

---

## 📜 Notes
- Replace `your_generated_jwt_token` with the actual token received from login.
- The backend supports multiple LLM models; specify the `model_name` accordingly.
- **Ensure your Railway service is running** for API access.

---

## 🛠️ Future Enhancements
- Add WebSocket support for real-time chat.
- Implement a better logging mechanism.
- Enhance security with OAuth2 scopes.
- Deploy a frontend interface to interact with the chatbot.

---

## 📞 Contact & Support
For any issues, feel free to reach out:
📧 **samarth.shinde505@gmail.com**
📌 **GitHub:** [SamarthShinde](https://github.com/SamarthShinde)

---

## 🚀 Changelog
### **Latest Updates (2025-02-19)**
- Added **Google Authentication** support.
- Integrated **OTP-based email verification** for secure registration.
- Improved **chat history storage** with timestamps.
- Optimized **requirements.txt** for production deployment.
- Fixed **CORS issues** for frontend compatibility.
- Enhanced **error handling** for better debugging.

---

This README reflects the latest changes and provides clear instructions for setup, deployment, and API usage. Let me know if you need further adjustments! 🚀