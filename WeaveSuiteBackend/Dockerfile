FROM python:3.11-slim

# Copy all files to app directory
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run database initialization and then launch the FastAPI application with uvicorn
CMD python src/db/database.py && uvicorn main:app --host 0.0.0.0 --port 8000