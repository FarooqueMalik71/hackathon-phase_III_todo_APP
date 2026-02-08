# 🚀 Hackathon Todo + AI Chatbot Startup Guide

## Quick Start

### 1. Start Backend (Port 8000)

```bash
cd /mnt/e/hackathon_todo_II/backend

# Option A: Using main.py (Recommended - includes both Todo + Chatbot)
uvicorn main:app --reload --port 8000

# Option B: Using new chatbot-only API
# uvicorn src.api.main:app --reload --port 8000
```

### 2. Start Frontend (Port 3000)

```bash
cd /mnt/e/hackathon_todo_II/frontend
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Chat Page**: http://localhost:3000/chat
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 Available API Endpoints

### Phase II Todo Endpoints
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{task_id}` - Get task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task

### AI Chatbot Endpoints
- `POST /api/{user_id}/chat` - Send chat message
- `GET /api/{user_id}/conversations` - List conversations
- `GET /api/{user_id}/conversations/{conversation_id}/messages` - Get messages
- `DELETE /api/{user_id}/conversations/{conversation_id}` - Delete conversation

---

## 🔧 Troubleshooting 404 Errors

### Issue: GET /api/{userId}/conversations returns 404

**Cause**: Running wrong backend or chatbot routes not loaded

**Solutions**:

#### Solution 1: Verify Backend is Running
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check available routes
curl http://localhost:8000/docs
```

#### Solution 2: Restart Backend with Correct Entry Point
```bash
cd /mnt/e/hackathon_todo_II/backend

# Stop any running backend (Ctrl+C)

# Start with integrated backend (Todo + Chatbot)
uvicorn main:app --reload --port 8000
```

#### Solution 3: Check Backend Logs
Look for these messages on startup:
```
✅ Chatbot API routes loaded
✅ MCP tools registered
```

If you see:
```
⚠️  Chatbot features not available
```

Then run:
```bash
cd /mnt/e/hackathon_todo_II/backend
pip install -r requirements.txt
```

---

## 🧪 Testing the Chatbot API

### Test with curl

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. List conversations (will be empty initially)
curl http://localhost:8000/api/user123/conversations \
  -H "Authorization: Bearer user123"

# 3. Send a chat message
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer user123" \
  -d '{
    "conversation_id": null,
    "message": "Add a task to buy groceries"
  }'
```

### Expected Response
```json
{
  "conversation_id": 1,
  "response": "I've added the task to your list!",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"title": "Buy groceries", "user_id": "user123"},
      "result": {"success": true, "task_id": "..."}
    }
  ],
  "response_time": 1.23
}
```

---

## 📝 Environment Variables

Create a `.env` file in `/backend/`:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hackathon_todo

# OpenRouter AI
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL=mistralai/mistral-7b-instruct

# Security
SECRET_KEY=your-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 🔑 Common Issues

### 1. 404 on /api/{userId}/conversations
**Fix**: Make sure you're running `uvicorn main:app`, not just `python main.py`

### 2. Import Errors on Backend Startup
**Fix**:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Errors
**Fix**:
```bash
cd backend
python -m src.database.migrations
```

### 4. Frontend Can't Connect to Backend
**Fix**: Check CORS settings in `.env`:
```
CORS_ORIGINS=http://localhost:3000
```

### 5. OpenAI API Errors
**Fix**: Set your OpenRouter API key in `.env`:
```
OPENAI_API_KEY=your-key-here
```

---

## 🎯 Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] `curl http://localhost:8000/docs` shows API documentation
- [ ] Can access http://localhost:3000/chat in browser
- [ ] No 404 errors in browser console
- [ ] Environment variables configured

---

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                  │
│                   http://localhost:3000                 │
│                                                         │
│  Routes:                                                │
│  - /chat           → AI Chatbot Interface              │
│  - /dashboard      → Todo Dashboard                     │
│  - /auth/login     → Login Page                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                     │
│                   http://localhost:8000                 │
│                                                         │
│  Main App (main.py)                                     │
│  ├── Phase II Routes (/api/v1/tasks)                   │
│  ├── Phase II Routes (/api/v1/auth)                    │
│  ├── Chatbot Routes (/api/{user_id}/chat)             │
│  └── Conversation Routes (/api/{user_id}/conversations)│
│                                                         │
│  Services:                                              │
│  ├── TaskIntegrationService → Existing Todo DB         │
│  ├── ChatService           → Conversation/Message DB   │
│  └── AIAgentService        → OpenRouter API            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎉 Success Indicators

When everything is working correctly, you should see:

**Backend Console:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ Chatbot API routes loaded
✅ MCP tools registered
```

**Frontend Console:**
```
✔ Ready in 2.5s
○ Local:   http://localhost:3000
```

**Browser:**
- No 404 errors in Network tab
- Chat interface loads at /chat
- Can send messages and get AI responses

---

## 💡 Pro Tips

1. **Use FastAPI Docs**: Visit http://localhost:8000/docs to test APIs interactively
2. **Check Browser Console**: F12 → Console tab for frontend errors
3. **Check Network Tab**: F12 → Network tab to see API requests/responses
4. **Use curl for Testing**: Test backend endpoints directly before frontend integration
5. **Check Backend Logs**: Terminal running uvicorn shows all API requests

---

Need help? Check:
- Backend logs for import errors
- Frontend console for network errors
- Database migrations are run
- Environment variables are set
