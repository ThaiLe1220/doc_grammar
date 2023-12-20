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
python -m venv venv
# On Windows (cmd)
venv\Scripts\activate
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On Unix or MacOS
source venv/bin/activate
```

Install the required Python packages:

```sh
pip install flask Flask-Uploads Werkzeug Flask-SQLAlchemy psycopg2-binary requests python-docx nltk authlib Flask-Login Flask-Migrate python-dotenv
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

## Structure
doc_grammar/
|-- my_flask_app/
|   |-- auth/
|       |-- __init__.py
|       |-- app.py
|       |-- Dockerfile
|       |-- entrypoint.sh
|       |-- login_manager.py
|       |-- oauth.py
|       |-- requirements.txt
|   |-- database/
|       |-- __init__.py
|       |-- db_setup.py
|   |-- file_handling/
|       |-- __init__.py
|       file_routes.py
|   |-- file_uploads/
|   |-- migrations/
|   |-- shared/
|       |-- __init__.py
|       |-- models.py
|   |-- static/
|       |-- css/
|            |-- style.css
|       |-- js/
|            |-- main.js
|   |-- templates/
|       |-- index.html
|   |-- tests/
|   |-- utils/
|       |-- __init__.py
|       |-- docx_utils.py
|       |-- grammar_checker.py
|       |-- reconstruct_sentence.py
|   |-- app.py
|-- venv/
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- README.md


