# Dockerfile

# 1. Base Image: Use a minimal Python image
FROM python:3.9-slim-bullseye

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
WORKDIR $APP_HOME

# 3. Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#5 
COPY main.py .
COPY svd_goodreads_model.pkl .
COPY book_id_to_title.json .

# 6. Expose the port the application will run on
EXPOSE 8000

# 7. Run the application using Gunicorn/Uvicorn (a robust setup for production)
# We use uvicorn managed by gunicorn for production stability and multiple worker processes
# Adjust the number of workers based on your target environment's CPU cores.
CMD ["/bin/sh", "-c", "gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker"]
