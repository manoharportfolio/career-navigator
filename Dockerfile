# Use official Python runtime
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# Run Flask with Gunicorn
CMD ["gunicorn", "-b", ":8080", "backend.app:app"]
