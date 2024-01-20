# DocGrammar

DocGrammar is a Flask web application designed to allow users to upload `.docx` files and automatically check for grammar errors. The application provides correction suggestions and allows users to download the corrected document.

## Features

- File Upload: Users can upload .docx files.
- Grammar Correction: The app automatically checks and suggests grammar corrections.
- Download Corrected Files: Users can download their improved documents.
- OAuth Integration: Secure sign-in with Google.
- Persistent Data Storage: Using PostgreSQL for storing file and user data.
- Modular Flask Structure: Organized code with Blueprints and modular design.

## Installation

To set up the project environment and run the application locally, follow these steps:

### Prerequisites

- Python 3
- pip
- Virtual environment
- PostgreSQL

### Setting Up the Environment

Clone the repository to your local machine and navigate to the project directory:

```sh
git clone https://github.com/ThaiLe1220/doc_grammar
cd doc_grammar/my_flask_app
```

Create and activate a virtual environment:

```sh
python3 -m venv venv
# On Windows (cmd)
venv\Scripts\activate
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On Unix or MacOS
source venv/bin/activate
```

Install the required Python packages:

```sh
pip3 install flask Flask-Uploads Werkzeug Flask-SQLAlchemy psycopg2-binary requests python-docx nltk authlib Flask-Login Flask-Migrate "Flask[async]" stripe aiohttp mod_wsgi boto3 pytz 
```

### Database Configuration

Ensure you have PostgreSQL installed and running. Create a new database and user with the following commands in the PostgreSQL shell:

```sql
CREATE USER username WITH PASSWORD 'password';
CREATE DATABASE doc_grammar;
GRANT ALL PRIVILEGES ON DATABASE doc_grammar TO username;
```

Run the following SQL commands to set up the necessary tables:

```sql
\c doc_grammar
CREATE TABLE file_uploads (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    corrections JSONB
);
```

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO username;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO username;

```

### Running the Application

Before running the application for the first time, make sure to set up the database with Flask-Migrate:

```sh
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

With the environment set up and the database migrations applied, you can start the Flask server:

```sh
python app.py
```

The application will be accessible at `http://localhost:5000`.

## Usage

1. Navigate to `http://localhost:5000` in your web browser.
2. Upload a `.docx` file using the provided form.
3. View the grammar corrections displayed on the page.
4. Download the corrected file if necessary.

## Contributing

If you'd like to contribute to the project, please fork the repository and create a pull request with your changes.

## License

This project is open source and available under the [MIT License](LICENSE.md).

## Acknowledgements

- Flask for the web framework.
- SQLAlchemy for ORM support.
- NLTK for natural language processing.
- psycopg2-binary for PostgreSQL adapter.

## Customize Functionality for different Roles
- Free: upload file up to 1 MB + 10 times/per day
- Basic: upload file up to 10 MB + 50 times/per day
- Premium: upload file up to 20 MB + 100 times/per day
- Note: pip install pytz due to the use of UTC 7+ vietnam



