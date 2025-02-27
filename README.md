# CSSE6400 Week 1 Practical

## Todo API

This project implements a simple HTTP REST API for a Todo application using Flask. The API provides endpoints to create, read, update, and delete todo items.

## Setup and Running

1. Install the dependencies: pip install flask

2. Run the application: python -m flask --app todo run --host=0.0.0.0 --port=6400

3. The API will be available at http://localhost:6400

## API Endpoints

### Health Check
- `GET /api/v1/health`
- Returns the status of the API
- Example: `curl http://localhost:6400/api/v1/health`

### List All Todos
- `GET /api/v1/todos`
- Returns a list of all todo items
- Example: `curl http://localhost:6400/api/v1/todos`

### Get a Specific Todo
- `GET /api/v1/todos/{id}`
- Returns details of a specific todo item
- Example: `curl http://localhost:6400/api/v1/todos/1`

### Create a Todo
- `POST /api/v1/todos`
- Creates a new todo item
- Example: `curl -X POST -H "Content-Type: application/json" -d '{"title":"Test Todo"}' http://localhost:6400/api/v1/todos`

### Update a Todo
- `PUT /api/v1/todos/{id}`
- Updates an existing todo item
- Example: `curl -X PUT -H "Content-Type: application/json" -d '{"title":"Updated Todo"}' http://localhost:6400/api/v1/todos/1`

### Delete a Todo
- `DELETE /api/v1/todos/{id}`
- Deletes a todo item
- Example: `curl -X DELETE http://localhost:6400/api/v1/todos/1`

## Implementation Details

This is an initial implementation with hardcoded responses. In future weeks, we will enhance the API with database integration and additional features.


