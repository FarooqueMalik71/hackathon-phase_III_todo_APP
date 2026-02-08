# Hackathon Todo Backend

This is the backend service for the Hackathon Todo Application, built with FastAPI and SQLModel.

## Features

- JWT-based authentication compatible with Better Auth
- Secure user isolation (users can only access their own tasks)
- RESTful API with full CRUD operations for tasks
- Proper error handling with consistent response formats
- Async database operations with Neon Serverless PostgreSQL
- Production-ready Docker configuration for Hugging Face Spaces
- Rate limiting and enhanced security features

## Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLModel for database operations
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT-based using Better Auth compatible tokens
- **API Version**: v1 with RESTful endpoints
- **Deployment**: Docker container for Hugging Face Spaces

## Environment Variables

The application requires the following environment variables:

```bash
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
BETTER_AUTH_SECRET=your_secret_key
BETTER_AUTH_URL=https://your-frontend-url.vercel.app  # For production
ENVIRONMENT=production  # Set to 'production' for production deployment
```

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Production Deployment (Hugging Face Spaces)

### Using Docker

The application is configured for deployment to Hugging Face Spaces:

1. The Dockerfile is configured to run on port 7860 (required by Hugging Face Spaces)
2. Build the Docker image:
   ```bash
   docker build -t hackathon-todo-backend .
   ```
3. Run locally for testing:
   ```bash
   docker run -p 7860:7860 -e DATABASE_URL="..." -e BETTER_AUTH_SECRET="..." -e BETTER_AUTH_URL="..." hackathon-todo-backend
   ```

### Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Choose "Docker" as the SDK
3. Add your repository as the source
4. Set the required environment variables in Space settings:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`
   - `BETTER_AUTH_URL` (your frontend URL)
   - `ENVIRONMENT=production`
5. The Space will automatically build and deploy using the provided Dockerfile

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint for production monitoring

### Authentication Required

All endpoints except the root (`/`) and health (`/health`) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Available Endpoints

- `GET /api/v1/tasks` - List user's tasks with optional filtering
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update a specific task
- `DELETE /api/v1/tasks/{task_id}` - Delete a specific task
- `PATCH /api/v1/tasks/{task_id}/toggle` - Toggle task completion status

## Error Handling

The API returns consistent error responses:

- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: Access to resource denied (cross-user access attempt)
- `404 Not Found`: Requested resource not found
- `422 Validation Error`: Request validation failed
- `500 Internal Server Error`: Unexpected server error
- `429 Too Many Requests`: Rate limit exceeded

## Security

- JWT tokens are validated using the Better Auth secret
- All queries are scoped to authenticated user's data
- Input validation is performed using Pydantic models
- Rate limiting to prevent abuse
- Proper HTTP status codes for all error conditions
- CORS configured appropriately for production