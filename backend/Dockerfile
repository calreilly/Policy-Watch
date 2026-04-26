FROM python:3.9-slim

WORKDIR /app

# System dependencies for ChromaDB & NetworkX
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize structure volumes
RUN mkdir -p /app/chromadb_data
RUN mkdir -p /app/memory_db

EXPOSE 8001

# Run Uvicorn directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
