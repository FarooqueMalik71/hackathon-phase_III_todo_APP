"""
Main FastAPI application for AI chatbot
Configures and runs the FastAPI server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from .v1.chat_endpoints import router as chat_router
from .v1.conversation_endpoints import router as conversation_router

# Import tools to register them
from ..tools import task_tools  # This auto-registers the tools

# Import config validation
from ..config import validate_config

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Todo Chatbot API",
    description="Natural language interface for todo list management",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(conversation_router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    try:
        # Validate configuration
        validate_config()
        print("✅ Configuration validated")
        print("✅ MCP tools registered")
        print("✅ AI chatbot API is ready!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Todo Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
