# URL Shortener API

A production-ready URL shortening API built with Flask, PostgreSQL, and SQLAlchemy. This API allows users to shorten long URLs, retrieve original links, and perform full CRUD operations on stored URLs.

## Features

- **URL Shortening**: Convert long URLs to short, manageable codes
- **Duplicate Prevention**: Same URLs return the same short code
- **Expiration Support**: Optional expiration dates for URLs
- **Analytics**: Track click counts for each shortened URL
- **Full CRUD Operations**: Create, read, update, and delete URLs
- **Input Validation**: Comprehensive validation using Marshmallow
- **Error Handling**: Proper HTTP status codes and error messages
- **Unit Tests**: Complete test coverage with pytest

## Tech Stack

- **Python 3.x**
- **Flask** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **Marshmallow** - Serialization and validation
- **pytest** - Testing framework
- **gunicorn** - Production WSGI server

## Project Structure

```
url-shortener-app/
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   ├── schemas.py           # Marshmallow schemas
│   ├── utils.py             # Utility functions
│   └── error_handlers.py    # Error handlers
│
├── tests/
│   └── test_app.py          # Unit tests
│
├── migrations/              # Database migrations
├── app.py                   # Application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── postman_collection.json  # API testing collection
└── README.md               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### 1. Clone the Repository

```bash
git clone <repository-url>
cd url-shortener-app
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

### 4. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE url_shortener;
CREATE DATABASE url_shortener_test;  # For testing
```

### 5. Environment Configuration

Create a `.env` file in the project root by copying the example:

```bash
cp env.example .env
```

Then edit the `.env` file with your actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/url_shortener

# PostgreSQL Database Settings (for setup_postgres.py)
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_PORT=5432
DB_NAME=url_db

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Application Configuration
BASE_URL=http://localhost:5000
```

**⚠️ Important:** Never commit your `.env` file to version control. It contains sensitive information!

### 6. Database Migrations

Initialize and run migrations:

```bash
python -m flask db init
python -m flask db migrate -m "Initial migration"
python -m flask db upgrade
```

### 7. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Shorten URL
**POST** `/shorten`

Shorten a long URL.

**Request Body:**
```json
{
    "long_url": "https://www.example.com/very/long/url/that/needs/shortening",
    "expires_at": "2024-12-31T23:59:59Z"  // Optional
}
```

**Response:**
```json
{
    "short_url": "http://localhost:5000/abc123"
}
```

### 2. Redirect to Original URL
**GET** `/<short_code>`

Redirect to the original URL.

**Response:** HTTP 302 redirect to the original URL

### 3. Get All URLs
**GET** `/urls`

Retrieve all stored URLs.

**Response:**
```json
{
    "urls": [
        {
            "id": 1,
            "long_url": "https://www.example.com",
            "short_code": "abc123",
            "click_count": 5,
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": null,
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

### 4. Get Specific URL
**GET** `/urls/<short_code>`

Get details of a specific URL.

**Response:**
```json
{
    "id": 1,
    "long_url": "https://www.example.com",
    "short_code": "abc123",
    "click_count": 5,
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": null,
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 5. Update URL
**PUT** `/urls/<short_code>`

Update a URL's destination.

**Request Body:**
```json
{
    "long_url": "https://www.newexample.com/updated/url",
    "expires_at": "2024-12-31T23:59:59Z"  // Optional
}
```

### 6. Delete URL
**DELETE** `/urls/<short_code>`

Delete a URL.

**Response:**
```json
{
    "message": "URL deleted successfully"
}
```

### 7. Get Analytics
**GET** `/analytics/<short_code>`

Get click analytics for a URL.

**Response:**
```json
{
    "short_code": "abc123",
    "clicks": 5
}
```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **410 Gone**: URL has expired
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server errors

Example error response:
```json
{
    "error": "Validation Error",
    "message": "Invalid input data",
    "details": {
        "long_url": ["Invalid URL format"]
    }
}
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Database Schema

### URLs Table

| Column      | Type      | Constraints           | Description                    |
|-------------|-----------|----------------------|--------------------------------|
| id          | INTEGER   | PRIMARY KEY          | Unique identifier              |
| long_url    | TEXT      | UNIQUE, NOT NULL     | Original long URL              |
| short_code  | VARCHAR   | UNIQUE, NOT NULL     | Generated short code           |
| click_count | INTEGER   | DEFAULT 0            | Number of clicks               |
| created_at  | DATETIME  | DEFAULT NOW          | Creation timestamp             |
| expires_at  | DATETIME  | NULLABLE             | Expiration timestamp           |
| updated_at  | DATETIME  | DEFAULT NOW, ON UPDATE| Last update timestamp         |

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
```

## API Testing with Postman

Import the `postman_collection.json` file into Postman to test all endpoints with pre-configured requests.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
