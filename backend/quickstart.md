# Backend Quickstart Guide

This guide will help you set up and run the Hackathon Todo Backend service.

## Prerequisites

- Python 3.9 or higher
- Neon Serverless PostgreSQL account
- Better Auth account (for JWT tokens)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
BETTER_AUTH_SECRET=your_secret_key
BETTER_AUTH_URL=http://localhost:3000
```

### 5. Run the Application

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Usage

### Authentication

All endpoints (except `/`) require a JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
     http://localhost:8000/api/v1/tasks
```

### Example Requests

#### Create a Task

```bash
curl -X POST \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Task description", "priority": "medium"}' \
  http://localhost:8000/api/v1/tasks
```

#### List Tasks

```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
     "http://localhost:8000/api/v1/tasks?completed=false&limit=10"
```

#### Update a Task

```bash
curl -X PUT \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task title", "completed": true}' \
  http://localhost:8000/api/v1/tasks/<task-id>
```

#### Toggle Task Completion

```bash
curl -X PATCH \
  -H "Authorization: Bearer <your-jwt-token>" \
  http://localhost:8000/api/v1/tasks/<task-id>/toggle
```

## Testing

To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**: Verify your `DATABASE_URL` is correct and accessible
2. **JWT Authentication Issues**: Ensure your `BETTER_AUTH_SECRET` matches your Better Auth configuration
3. **CORS Issues**: Check that `BETTER_AUTH_URL` matches your frontend origin

### Development Tips

- Use `--reload` flag with uvicorn for auto-reload during development
- Enable logging in the database session by setting `echo=True`
- Check the `/docs` endpoint for interactive API documentation

## Next Steps

1. Integrate with your frontend application
2. Set up authentication with Better Auth
3. Configure your database in production
4. Set up monitoring and logging