from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

class Notes(BaseModel):
    text: str


@app.post("/summarize")
def summarize_notes(notes: Notes):

    API_URL = "https://router.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": notes.text
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if response.status_code == 200 and isinstance(result, list):
        summary = result[0]["summary_text"]
    else:
        summary = result.get("error", result)

    return {
        "status_code": response.status_code,
        "summary": summary
    }
