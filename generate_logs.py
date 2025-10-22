import json
import random
import time
from faker import Faker
from google.cloud import storage

# --- Configuration ---
NUM_RECORDS = 2000000  # Generate 2 million records (approx 1GB of data)
OUTPUT_FILENAME = "web_server_logs.json"
GCS_BUCKET_NAME = "raw-logs-bucket"
GCS_BLOB_PATH = "raw-logs-bucket/2025/10/22/web_server_logs.json"
# Initialize Faker and GCS client
fake = Faker()
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)
blob = bucket.blob(GCS_BLOB_PATH)

# --- Data Generation Function ---
def generate_fake_log():
    """Generates a single structured log entry."""
    return {
        "timestamp": int(time.time() - random.randint(0, 86400)), # Time in the last 24 hours
        "user_id": fake.uuid4(),
        "event_type": random.choice(["PAGE_VIEW", "CLICK", "ERROR", "PURCHASE"]),
        "url_path": random.choice(["/home", "/product/widget", "/checkout", "/login", "/blog/post-101"]),
        "latency_ms": random.randint(10, 5000), # Latency in milliseconds
        "browser": random.choice(["Chrome", "Safari", "Firefox"])
    }

# --- Write to GCS ---
print(f"Generating {NUM_RECORDS} records...")
records = [generate_fake_log() for _ in range(NUM_RECORDS)]

# Write all records to a single string/JSON line by line
json_data = "\n".join(json.dumps(r) for r in records)

print("Uploading data to GCS...")
blob.upload_from_string(json_data, content_type="application/json")

print(f"✅ Data successfully uploaded to gs://{GCS_BUCKET_NAME}/{GCS_BLOB_PATH}")