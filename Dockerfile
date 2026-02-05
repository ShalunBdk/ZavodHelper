FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Initialize database and run
CMD ["sh", "-c", "python scripts/init_db.py && python run.py"]
