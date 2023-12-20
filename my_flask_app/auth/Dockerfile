# Dockerfile - Directory: my_flask_app/auth  

FROM python:3.8-slim

RUN apt-get update && apt-get install -y netcat-openbsd
WORKDIR /app

COPY ./auth /app
COPY ./app/migrations /app/migrations
COPY ./database /app/database

COPY ./auth/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
ENV FLASK_APP auth/auth_app.py
COPY auth/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
