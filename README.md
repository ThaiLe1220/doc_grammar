# DocGrammar

DocGrammar is a Flask web application designed to allow users to upload `.docx` files and automatically check for grammar errors. The application provides correction suggestions and allows users to download the corrected document.

## Features

- File upload functionality for `.docx` files.
- Automatic grammar checking with detailed suggestions.
- Ability to download the corrected document.
- Persistent storage of uploaded files and correction details in a PostgreSQL database.

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
git clone <repository-url>
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
pip install flask Flask-Uploads Werkzeug Flask-SQLAlchemy psycopg2-binary requests python-docx nltk
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

### Running the Application

With the environment set up and the database configured, you can start the Flask server:

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

