import pickle
import json
from fastapi import FastAPI, HTTPException
from surprise import SVD, Dataset, Reader
from typing import List
import os # <-- Import os

os.chdir('/app')

# --- Configuration ---
MODEL_PATH = 'svd_goodreads_model.pkl'
MAPPING_PATH = 'book_id_to_title.json'

# --- Initialization ---
app = FastAPI(title="GoodReads Real-Time Recommender")

# Global variables to store the loaded artifacts
MODEL = None
BOOK_MAP = None

def load_artifacts():
    """Load the trained model and the book title mapping once at startup."""
    global MODEL, BOOK_MAP
    try:
        # Load the model (using pickle, adjust to joblib if needed)
        with open(MODEL_PATH, 'rb') as file:
            MODEL = pickle.load(file)
            
        # Load the book mapping (ID to Title)
        with open(MAPPING_PATH, 'r') as file:
            BOOK_MAP = json.load(file)
            
        print("✅ Model and mapping loaded successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ ERROR: Artifact file not found: {e}")
        # The app should ideally fail to start if the model isn't there
        raise

def get_recommendations_for_user(user_id: int) -> List[str]:
    """Generates the top N book recommendations for a given user ID."""
    
    # 1. Get a list of all unique book IDs known to the model
    # Note: In Surprise, item IDs are internal, so we use the keys from the saved map
    all_book_ids = list(BOOK_MAP.keys())
    
    # 2. Get the books the user has already rated (or interacted with)
    # The trained model has an internal mapping for user IDs, so we need to
    # check if the user exists in the model's structure before proceeding.
    try:
        # This is a robust way to check if a user is known to the full training set
        user_inner_id = MODEL.trainset.to_inner_uid(user_id) 
    except ValueError:
        # If the user ID is not in the training set (e.g., a cold start problem)
        raise HTTPException(
            status_code=404, 
            detail=f"User ID {user_id} not found or inactive in the training data."
        )

    # In a real-world scenario, you'd load the user's past ratings.
    # For this project, we'll assume we only recommend books the user *hasn't* rated (for simplicity).
    
    # 3. Predict the rating for ALL books the user hasn't rated
    predictions = []
    for item_id_str in all_book_ids:
        item_id = int(item_id_str) # Ensure item ID is integer if needed by the model
        
        # We assume for this simple setup that every ID in BOOK_MAP is a potential item.
        # A more complex check would look up the user's history and skip rated items.
        # For simplicity, we predict for all, and the model inherently gives low scores 
        # to items that aren't good fits.
        
        predicted_rating = MODEL.predict(user_id, item_id).est
        predictions.append((item_id, predicted_rating))

    # 4. Sort predictions and get the top N
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n_predictions = predictions[:TOP_N]

    # 5. Convert IDs to Titles
    recommendation_titles = [BOOK_MAP[str(book_id)] for book_id, _ in top_n_predictions]

    return recommendation_titles

# --- FastAPI Lifespan (Startup) ---
@app.on_event("startup")
def startup_event():
    """Load model artifacts when the application starts."""
    load_artifacts()


# --- API Endpoint ---
@app.get("/recommendations/{user_id}", response_model=List[str], tags=["Recommendations"])
async def get_user_recommendations(user_id: int):
    """
    Returns the top 10 recommended book titles for the given user ID.
    """
    if MODEL is None or BOOK_MAP is None:
        raise HTTPException(status_code=500, detail="Model service not yet initialized.")
        
    try:
        recommendations = get_recommendations_for_user(user_id)
        return recommendations
    except HTTPException as e:
        # Re-raise the 404 error if user is not found
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during recommendation generation.")

# --- Root Endpoint (Health Check) ---
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "GoodReads Recommender API is running."}