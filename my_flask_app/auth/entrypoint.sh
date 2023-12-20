#!/bin/bash

# entrypoint.sh - Directory: my_flask_app/auth  

# Function to check database readiness
check_database_readiness() {
    while ! nc -z db 5432; do
        echo "Database is not yet available - sleeping"
        sleep 1
    done
    echo "Database is ready!"
}

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
check_database_readiness

# Run database migrations
echo "Running database migrations..."
flask db init
flask db migrate -m "Initial migration."
flask db upgrade

# Start the Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0
