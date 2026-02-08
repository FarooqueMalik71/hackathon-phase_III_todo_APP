# Quickstart Guide: AI-Powered Todo Chatbot

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database
- OpenRouter API key
- Existing Phase II todo application backend services

## Environment Setup

### Backend
1. Install Python dependencies:
```bash
pip install fastapi uvicorn openrouter-python python-jose[cryptography] passlib[bcrypt] psycopg2-binary
```

2. Set environment variables:
```bash
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="your-openrouter-key"
export MODEL="mistralai/mistral-7b-instruct"
export DATABASE_URL="postgresql://username:password@localhost/dbname"
export SECRET_KEY="your-secret-key"
```

3. Run database migrations:
```bash
# Execute migration scripts to create Conversation and Message tables
```

### Frontend
1. Install Node.js dependencies:
```bash
npm install
```

2. Ensure backend API endpoints are accessible

## Running the Application

### Backend
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Frontend
```bash
npm run dev
```

## API Endpoints

### Chat Endpoint
- `POST /api/{user_id}/chat`
- Request: `{ "conversation_id": number, "message": string }`
- Response: `{ "conversation_id": number, "response": string, "tool_calls": array }`

### Conversation Endpoints
- `GET /api/{user_id}/conversations`
- `GET /api/{user_id}/conversations/{conversation_id}/messages`

## MCP Tool Server
Start the MCP tool server separately:
```bash
python src/tools/mcp_server.py
```

## Testing
Run backend tests:
```bash
pytest tests/
```

Run frontend tests:
```bash
npm test
```

## Key Components
1. **Chat Service**: Handles conversation flow and history
2. **AI Agent Service**: Processes natural language and selects tools
3. **MCP Tool Service**: Executes task operations via existing services
4. **Chat Interface**: Frontend component for user interaction