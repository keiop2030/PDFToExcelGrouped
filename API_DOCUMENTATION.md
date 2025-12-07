# API Documentation

This document describes the REST API endpoints available in the PDF to Excel Grouped Converter application.

## Base URL

When running locally: `http://localhost:5000`

## Authentication

Most API endpoints require authentication. After logging in via the `/auth/api/login` endpoint, the session cookie will be automatically included in subsequent requests.

## Endpoints

### Authentication

#### Register a New User

**POST** `/auth/api/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-11-07T10:30:00"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Username already exists"
}
```

---

#### Login

**POST** `/auth/api/login`

Authenticate a user and create a session.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-11-07T10:30:00"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid username or password"
}
```

---

### Projects

#### List All Projects

**GET** `/projects/api/projects`

Get all projects for the authenticated user.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Q4 Bank Statements",
      "description": "Bank statements for Q4 2024",
      "user_id": 1,
      "created_at": "2024-11-07T10:45:00",
      "updated_at": "2024-11-07T11:30:00",
      "file_count": 3
    },
    {
      "id": 2,
      "name": "Q3 Expenses",
      "description": "Expense reports for Q3",
      "user_id": 1,
      "created_at": "2024-10-15T09:20:00",
      "updated_at": "2024-10-20T14:15:00",
      "file_count": 5
    }
  ]
}
```

---

#### Create a New Project

**POST** `/projects/api/projects`

Create a new project for the authenticated user.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Q4 Bank Statements",
  "description": "Bank statements for the fourth quarter of 2024"
}
```

**Response (201 Created):**
```json
{
  "message": "Project created successfully",
  "project": {
    "id": 1,
    "name": "Q4 Bank Statements",
    "description": "Bank statements for the fourth quarter of 2024",
    "user_id": 1,
    "created_at": "2024-11-07T10:45:00",
    "updated_at": "2024-11-07T10:45:00",
    "file_count": 0
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Project name is required"
}
```

---

#### Get Project Details

**GET** `/projects/api/projects/{project_id}`

Get details of a specific project, including all uploaded files.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "project": {
    "id": 1,
    "name": "Q4 Bank Statements",
    "description": "Bank statements for the fourth quarter of 2024",
    "user_id": 1,
    "created_at": "2024-11-07T10:45:00",
    "updated_at": "2024-11-07T11:30:00",
    "file_count": 2,
    "files": [
      {
        "id": 1,
        "filename": "20241107_103000_statement.pdf",
        "original_filename": "statement.pdf",
        "project_id": 1,
        "status": "completed",
        "excel_path": "/uploads/1/20241107_103000_statement.xlsx",
        "uploaded_at": "2024-11-07T10:30:00",
        "processed_at": "2024-11-07T10:30:15"
      },
      {
        "id": 2,
        "filename": "20241107_113000_transactions.pdf",
        "original_filename": "transactions.pdf",
        "project_id": 1,
        "status": "completed",
        "excel_path": "/uploads/1/20241107_113000_transactions.xlsx",
        "uploaded_at": "2024-11-07T11:30:00",
        "processed_at": "2024-11-07T11:30:20"
      }
    ]
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": "Access denied"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Project not found"
}
```

---

#### Delete a Project

**DELETE** `/projects/api/projects/{project_id}`

Delete a project and all associated files.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Project deleted successfully"
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": "Access denied"
}
```

---

### File Operations

#### Download Excel File

**GET** `/projects/download/{file_id}`

Download the processed Excel file for a specific PDF upload.

**Authentication:** Required

**Response:** Binary Excel file (`.xlsx`)

**Headers:**
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="output.xlsx"`

---

## Web Form Endpoints

The following endpoints accept form data for file uploads:

#### Upload PDF File

**POST** `/projects/{project_id}/upload`

Upload and process a PDF file within a project.

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: PDF file (required)

**Response:** HTTP 302 Redirect to project detail page with flash message

---

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created successfully |
| 302  | Redirect (form submissions) |
| 400  | Bad request (validation error) |
| 401  | Unauthorized (login required) |
| 403  | Forbidden (access denied) |
| 404  | Not found |
| 500  | Internal server error |

---

## Example Usage with cURL

### Register a New User
```bash
curl -X POST http://localhost:5000/auth/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"testuser","password":"password123"}'
```

### Create a Project
```bash
curl -X POST http://localhost:5000/projects/api/projects \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"My Project","description":"Test project"}'
```

### List Projects
```bash
curl -X GET http://localhost:5000/projects/api/projects \
  -b cookies.txt
```

### Get Project Details
```bash
curl -X GET http://localhost:5000/projects/api/projects/1 \
  -b cookies.txt
```

### Upload PDF File
```bash
curl -X POST http://localhost:5000/projects/1/upload \
  -b cookies.txt \
  -F "file=@path/to/document.pdf"
```

### Download Excel File
```bash
curl -X GET http://localhost:5000/projects/download/1 \
  -b cookies.txt \
  -o output.xlsx
```

### Delete a Project
```bash
curl -X DELETE http://localhost:5000/projects/api/projects/1 \
  -b cookies.txt
```

---

## Example Usage with Python Requests

```python
import requests

BASE_URL = "http://localhost:5000"

# Create a session to persist cookies
session = requests.Session()

# Register
response = session.post(f"{BASE_URL}/auth/api/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# Login
response = session.post(f"{BASE_URL}/auth/api/login", json={
    "username": "testuser",
    "password": "password123"
})
print(response.json())

# Create a project
response = session.post(f"{BASE_URL}/projects/api/projects", json={
    "name": "My Project",
    "description": "Test project"
})
project = response.json()['project']
project_id = project['id']
print(f"Created project with ID: {project_id}")

# List all projects
response = session.get(f"{BASE_URL}/projects/api/projects")
print(response.json())

# Upload a PDF file
with open("document.pdf", "rb") as f:
    response = session.post(
        f"{BASE_URL}/projects/{project_id}/upload",
        files={"file": f}
    )

# Get project details (including file information)
response = session.get(f"{BASE_URL}/projects/api/projects/{project_id}")
project_details = response.json()['project']
print(project_details)

# Download the processed Excel file
if project_details['files']:
    file_id = project_details['files'][0]['id']
    response = session.get(f"{BASE_URL}/projects/download/{file_id}")
    with open("output.xlsx", "wb") as f:
        f.write(response.content)
    print("Downloaded Excel file")

# Delete the project
response = session.delete(f"{BASE_URL}/projects/api/projects/{project_id}")
print(response.json())
```

---

## Rate Limiting

Currently, there are no rate limits implemented. For production deployments, consider implementing rate limiting to prevent abuse.

## Notes

- All timestamps are in ISO 8601 format (UTC)
- File uploads are limited to 16MB
- Only PDF files are accepted for upload
- Session cookies expire when the browser is closed
- The API uses session-based authentication (cookies), not token-based authentication
