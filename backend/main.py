from fastapi import FastAPI
from api.v1 import tasks, auth
import os
from sqlmodel import SQLModel
from db.session import sync_engine

from core.security_config import add_security_middlewares

# Import models to register them with SQLModel
from models import user, task

# Import chatbot routers and tools
try:
    from src.api.v1.chat_endpoints import router as chat_router
    from src.api.v1.conversation_endpoints import router as conversation_router
    from src.tools import task_tools  # Auto-registers MCP tools
    CHATBOT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Chatbot features not available: {e}")
    CHATBOT_AVAILABLE = False

app = FastAPI(title="Hackathon Todo Backend", version="1.0.0" )

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(sync_engine)
    if CHATBOT_AVAILABLE:
        print("✅ Chatbot API routes loaded")
        print("✅ MCP tools registered")

# Add security middlewares
add_security_middlewares(app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hackathon Todo Backend"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# Include API routes
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

# Include chatbot routes (if available)
if CHATBOT_AVAILABLE:
    app.include_router(chat_router)
    app.include_router(conversation_router)
