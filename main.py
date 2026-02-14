from fastapi import FastAPI, Header, HTTPException
from google.cloud import firestore
from typing import List
import os

app = FastAPI()
db = firestore.Client()

API_KEY = os.environ.get("API_KEY")

@app.post("/expenses/batch")
async def create_expenses(expenses: List[dict], x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    batch = db.batch()

    for expense in expenses:
        message_id = expense["message_id"]
        ref = db.collection("expenses").document(message_id)
        batch.set(ref, expense)

    batch.commit()

    return {"status": "ok", "count": len(expenses)}
