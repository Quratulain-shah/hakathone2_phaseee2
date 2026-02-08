---
title: Todo App Backend API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Todo App Backend API

FastAPI backend for the Todo App with JWT authentication.

## Features

- User registration and authentication (JWT)
- CRUD operations for tasks
- PostgreSQL database (Neon Serverless)
- Async/await support

## Setup (Local Development)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export DATABASE_URL=postgresql+asyncpg://user:password@localhost/todo_app
   export SECRET_KEY=your-secret-key-here
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /api/v1/register` - Register a new user
- `POST /api/v1/login` - Login and get JWT token
- `GET /api/v1/me` - Get current user info

### Tasks
- `GET /api/v1/{user_id}/tasks` - List user's tasks
- `POST /api/v1/{user_id}/tasks` - Create a task
- `GET /api/v1/{user_id}/tasks/{task_id}` - Get a task
- `PUT /api/v1/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/v1/{user_id}/tasks/{task_id}` - Delete a task

## Hugging Face Deployment

Set these as **Secrets** in your Hugging Face Space settings:

- `DATABASE_URL` - PostgreSQL connection string (e.g., Neon)
- `SECRET_KEY` - JWT secret key for token signing

## API Documentation

Visit `/api/v1/docs` for Swagger UI documentation.

## Architecture

- FastAPI for the web framework
- SQLModel for database models and ORM
- Pydantic for request/response validation
- Async operations throughout
- User isolation pattern implemented
