# 🚀 Quick Start Guide - AI Chatbot

## ⚡ Start in 30 Seconds

```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev

# Browser
open http://localhost:3000/chat
```

---

## ✅ Verify Everything Works

### 1. Check Backend
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 2. Check Conversations
```bash
curl http://localhost:8000/api/user123/conversations \
  -H "Authorization: Bearer user123"
# Expected: []
```

### 3. Check Frontend
- Visit: http://localhost:3000/chat
- Should see: Chat interface with "Start a conversation" message
- Should NOT see: 404 errors or "Failed to load" errors

---

## 🐛 Troubleshooting

### Frontend Won't Build
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Backend Returns 404
```bash
cd backend
source venv/bin/activate  # or activate.bat on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Chat Returns 503
**Cause**: OpenRouter API issue
**Fix**:
1. Check `backend/.env` has valid `OPENAI_API_KEY`
2. Model is now: `openai/gpt-3.5-turbo` (supports tools)
3. Restart backend after .env changes

### Import Errors in Frontend
**Cause**: Missing files
**Status**: ✅ All files created
**Files**:
- ✅ `/frontend/src/types/chat.d.ts`
- ✅ `/frontend/src/services/api/chat_api.ts`
- ✅ `/frontend/src/components/chat/ChatInterface.tsx`

---

## 📝 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/api/{user_id}/conversations` | List conversations |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get messages |
| POST | `/api/{user_id}/chat` | Send message |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation |

---

## 🎯 Expected Behavior

### On Page Load
1. ✅ Sidebar shows "New Conversation" button
2. ✅ Main area shows "Start a conversation" message
3. ✅ Loading spinner briefly while fetching conversations
4. ✅ If conversations exist, they appear in sidebar

### On Sending Message
1. ✅ Message appears immediately in chat
2. ✅ Spinner shows while waiting for response
3. ✅ AI response appears with tool execution details
4. ✅ Conversation ID is created (for first message)
5. ✅ New conversation appears in sidebar

### On Error
1. ✅ Red alert box shows user-friendly error
2. ✅ Failed message is removed
3. ✅ Input remains enabled for retry

---

## 🎨 UI Features

- ✅ **Blue bubbles** for your messages (right side)
- ✅ **Gray bubbles** for AI responses (left side)
- ✅ **Tool badges** showing what AI did (e.g., "add task")
- ✅ **Timestamps** on all messages
- ✅ **Delete button** on hover (in sidebar)
- ✅ **Loading states** everywhere
- ✅ **Error messages** in red boxes
- ✅ **Auto-scroll** to latest message

---

## 🔑 Keyboard Shortcuts

- **Enter** → Send message
- **Shift+Enter** → New line
- **Click conversation** → Switch to that conversation
- **Click "New Conversation"** → Start fresh chat

---

## 📱 Mobile Support

- ✅ Responsive design
- ✅ Touch-friendly buttons
- ✅ Collapsible sidebar (in future update)
- ✅ Works on all screen sizes

---

## 🎉 Success Indicators

When everything is working, you should see:

**Backend Console**:
```
✅ Chatbot API routes loaded
✅ MCP tools registered
INFO: Uvicorn running on http://127.0.0.1:8000
```

**Frontend Console**:
```
✓ Ready in 2.5s
○ Local: http://localhost:3000
```

**Browser**:
- ✅ No errors in console (F12)
- ✅ Chat interface loads instantly
- ✅ Can send messages
- ✅ Messages appear immediately

---

## 💡 Tips

1. **First Time Setup**:
   - The conversation list will be empty initially
   - Just start typing and send a message
   - A new conversation will be created automatically

2. **Managing Conversations**:
   - Each conversation has a unique ID
   - Messages are persistent (saved in database)
   - Delete unwanted conversations with the trash icon

3. **AI Responses**:
   - May take 2-5 seconds
   - Will show what tools were used
   - May fail if OpenRouter API key is invalid

4. **Development Mode**:
   - Backend auto-reloads on code changes
   - Frontend auto-reloads on save
   - Database changes require restart

---

## 📚 Documentation

- **Full Report**: `CHATBOT_FINAL_REPORT.md`
- **Startup Guide**: `STARTUP_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **Test Script**: `backend/test_routes.sh`

---

**Need Help?**
1. Check browser console (F12) for errors
2. Check backend logs for API errors
3. Run `backend/test_routes.sh` to verify endpoints
4. Read `CHATBOT_FINAL_REPORT.md` for detailed info
