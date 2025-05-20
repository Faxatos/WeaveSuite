FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#set environment variable for Python path
ENV PYTHONPATH=/app

#load .env file and run the commands in sequence
CMD sh -c 'if [ -f .env ]; then export $(grep -v "^#" .env | xargs); fi && \
           echo "Initializing database..." && \
           python /app/src/db/database.py && \
           echo "Starting application..." && \
           python /app/src/launcher.py'