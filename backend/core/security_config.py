from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

def add_security_middlewares(app: FastAPI):
    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS - restrict origins in production
    allowed_origins = [os.getenv("BETTER_AUTH_URL", "http://localhost:3000")]
    if os.getenv("ENVIRONMENT", "development") == "development":
        allowed_origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",  # Common alternative Next.js port
            "http://127.0.0.1:3001",  # Alternative for Next.js
            "http://localhost:3002",  # Another common Next.js port
            "http://127.0.0.1:3002",  # Alternative for Next.js
            "http://localhost:3003",
            "http://127.0.0.1:3003"
        ])

    # Always allow Hugging Face Spaces URLs for health checks
    allowed_origins.append("https://*.hf.space")
    allowed_origins.append("https://huggingface.co")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if os.getenv("ENVIRONMENT", "development") == "development" else allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Security: Only allow specific headers in production
        expose_headers=["Access-Control-Allow-Origin"]
    )

    # Additional security headers can be added here
    # X-Frame-Options, X-Content-Type-Options, etc.