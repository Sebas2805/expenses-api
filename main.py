from fastapi import FastAPI, Header, HTTPException
from google.cloud import firestore
from typing import List
import os

app = FastAPI()
db = firestore.Client()

API_KEY = os.environ.get("API_KEY")

@app.post("/expenses/batch")
async def create_expenses(expenses: List[dict], x_api_key: str = Header(None)):

    # Auth check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Protect against empty payload
    if not expenses:
        return {"status": "no_data", "count": 0}

    # Protect against huge batches
    if len(expenses) > 100:
        raise HTTPException(status_code=400, detail="Batch too large")

    try:

        batch = db.batch()

        for expense in expenses:
            message_id = expense["message_id"]
            ref = db.collection("expenses").document(message_id)
            batch.set(ref, expense)

        batch.commit()

        return {
            "status": "ok",
            "count": len(expenses)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Firestore error: {str(e)}"
        )