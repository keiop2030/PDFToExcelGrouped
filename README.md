# PDFToExcelGrouped

Convert Bank PDFs into Excel files with intelligent grouping of similar/common lines.

## Features

- 🔐 **User Authentication**: Secure registration and login system
- 📁 **Project Management**: Organize PDF conversions into separate projects
- 📤 **PDF Upload**: Upload PDF files for processing
- 🤖 **Smart Grouping**: Automatically groups similar lines from PDFs using similarity algorithms
- 📊 **Excel Export**: Download organized data in Excel format with grouped lines
- 🎨 **Web Interface**: Clean and intuitive Flask web application
- 🔌 **REST API**: Full API support for programmatic access

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/keiop2030/PDFToExcelGrouped.git
cd PDFToExcelGrouped
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

### Web Interface

1. **Register an Account**: Navigate to `/auth/register` to create a new account
2. **Login**: Login at `/auth/login` with your credentials
3. **Create a Project**: From the dashboard, create a new project to organize your PDFs
4. **Upload PDF**: In the project detail page, upload a PDF file
5. **Download Excel**: Once processed, download the grouped Excel file

### API Endpoints

#### Authentication

**Register a new user**
```bash
POST /auth/api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

**Login**
```bash
POST /auth/api/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

#### Projects

**List all projects**
```bash
GET /projects/api/projects
```

**Create a new project**
```bash
POST /projects/api/projects
Content-Type: application/json

{
  "name": "Q4 Bank Statements",
  "description": "Bank statements for Q4 2024"
}
```

**Get project details**
```bash
GET /projects/api/projects/{project_id}
```

**Delete a project**
```bash
DELETE /projects/api/projects/{project_id}
```

## How It Works

### PDF Processing Algorithm

1. **Text Extraction**: Extracts all text lines from the PDF using pdfplumber
2. **Similarity Calculation**: Compares each line with others using sequence matching
3. **Grouping**: Groups lines with similarity ratio above threshold (default: 0.8)
4. **Excel Generation**: Creates an Excel file with:
   - Representative line for each group
   - Count of similar lines
   - All similar lines concatenated

### Grouping Example

Input PDF lines:
```
Payment to ABC Corp - Invoice 123
Payment to ABC Corp - Invoice 124
Transfer to Savings Account
Payment to ABC Corp - Invoice 125
```

Output Excel:
| Representative Line | Count | All Similar Lines |
|---------------------|-------|-------------------|
| Payment to ABC Corp - Invoice 123 | 3 | Payment to ABC Corp - Invoice 123 \| Payment to ABC Corp - Invoice 124 \| Payment to ABC Corp - Invoice 125 |
| Transfer to Savings Account | 1 | Transfer to Savings Account |

## Project Structure

```
PDFToExcelGrouped/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models (User, Project, PDFFile)
│   ├── pdf_processor.py      # PDF processing and grouping logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main routes (home, dashboard)
│   │   └── projects.py      # Project management routes
│   ├── static/
│   │   └── css/
│   │       └── style.css    # Application styles
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── projects.html
│       ├── create_project.html
│       └── project_detail.html
├── uploads/                 # Upload directory (created automatically)
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Schema

### User
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- created_at (DateTime)

### Project
- id (Integer, Primary Key)
- name (String)
- description (Text)
- user_id (Foreign Key → User)
- created_at (DateTime)
- updated_at (DateTime)

### PDFFile
- id (Integer, Primary Key)
- filename (String)
- original_filename (String)
- file_path (String)
- project_id (Foreign Key → Project)
- excel_path (String)
- status (String: uploaded, processing, completed, error)
- error_message (Text)
- uploaded_at (DateTime)
- processed_at (DateTime)

## Configuration

The application uses the following default configuration:

- **Database**: SQLite (pdftoexcel.db)
- **Upload Folder**: ./uploads
- **Max File Size**: 16MB
- **Secret Key**: Set via environment variable `SECRET_KEY` (default: dev-secret-key-change-in-production)

## Production Deployment

For production deployments, ensure the following:

1. **Set a secure SECRET_KEY**: 
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
   ```

3. **Use a production database** (PostgreSQL, MySQL) instead of SQLite

4. **Enable HTTPS** with a reverse proxy (nginx, Apache)

5. **Set proper file permissions** for uploads directory

6. **Configure firewall** and security groups appropriately

## Security Considerations

- Passwords are hashed using Werkzeug's security utilities
- File uploads are validated and sanitized
- Session management via Flask-Login
- CSRF protection recommended for production
- Never use default SECRET_KEY in production

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
