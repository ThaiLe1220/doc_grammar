# Dockerfile - Directory: my_flask_app/app

FROM python:3.8-slim

RUN apt-get update && apt-get install -y netcat-openbsd
WORKDIR /app

COPY ./app /app
COPY ./database /app/database

COPY ./app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Define environment variable
ENV FLASK_APP app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]