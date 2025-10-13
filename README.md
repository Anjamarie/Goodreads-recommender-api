# Real-Time Book Recommendation API (Full-Stack ML Engineering) 

This project demonstrates a complete, end-to-end Machine Learning deployment pipeline, serving personalized book recommendations in real-time via a FastAPI web service.

##  Live Deployment

| Service | Link |
| :--- | :--- |
| **Live API Endpoint** | **https://goodreads-recommender-418836917221.us-west3.run.app/** |
| **Interactive Docs (Swagger UI)** | **https://goodreads-recommender-418836917221.us-west3.run.app//docs** |

***

##  Project Goals and ML Core

The core objective was to build a low-latency, resilient service. This system provides real-time personalized book recommendations based on user history.

* **Dataset:** **GoodReads 10k** dataset, filtered to ensure high-quality, dense user-item interactions.
* **Model:** **Singular Value Decomposition (SVD)**, a foundational matrix factorization algorithm for Collaborative Filtering.
* **Performance:** Achieved an **RMSE of [Insert Your Recorded RMSE]** on the rating prediction task.

***

##  The Full Stack and Technologies

| Component | Technology | Role |
| :--- | :--- | :--- |
| **ML/Data** | Python, `scikit-surprise`, Pandas | Model training and artifact persistence. |
| **API Server** | FastAPI, Gunicorn, Uvicorn | High-performance ASGI web service. |
| **Containerization** | Docker, Buildx | Packaging the application for cross-platform portability. |
| **Deployment** | **Google Cloud Run (GCR)**, Artifact Registry | Serverless hosting, auto-scaling, and secure image hosting. |

***

## � Engineering Challenges and Solutions (High-Value Debugging)

The primary value of this project lies in the successful resolution of critical production deployment obstacles:

### 1. Platform Architecture Mismatch (ARM64 $\rightarrow$ AMD64)
* **Problem:** Building the Docker image on a Mac M-series (ARM64) without targeting the necessary architecture caused the image to fail on Cloud Run (which runs AMD64/Linux).
* **Solution:** Used the **`docker buildx build --platform linux/amd64`** command to explicitly compile a multi-architecture image, ensuring compatibility.

### 2. Dependency Conflict (NumPy 2.0 Incompatibility)
* **Problem:** The core ML library (`scikit-surprise`) crashed during startup due to incompatibility with the newest version of NumPy installed in the Docker environment.
* **Solution:** Explicitly **pinned the NumPy dependency** to a compatible version in `requirements.txt`: **`numpy<2.0.0`**.

### 3. Cloud Run Port & Memory Failures
* **Problem:** The service consistently failed the health check (**503 Service Unavailable**) because of conflicts between the application's required port and the platform's environmental settings, compounded by insufficient memory for model loading.
* **Solution:**
    * **Port Fix:** Used the robust shell form in the `Dockerfile` to bind Gunicorn directly to the platform's injected variable: **`--bind 0.0.0.0:$PORT`**.
    * **Resource Fix:** Increased the Cloud Run service memory allocation to **2 GiB** and reduced Gunicorn workers to overcome the initial model loading memory spike.

***

##  How to Run Locally

1.  Clone the repository:
    ```bash
    git clone [YOUR_GITHUB_REPO_URL]
    cd your-repo-name
    ```
2.  Build the image (Requires Docker Buildx):
    ```bash
    docker build -t local-recommender:latest .
    ```
3.  Run the container:
    ```bash
    docker run -d -p 8000:8000 local-recommender:latest
    ```
4.  Access the API documentation at: `http://localhost:8000/docs`
