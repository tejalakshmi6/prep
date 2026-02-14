from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
import logging
import re

# Configure logging
logging.basicConfig(
    filename='backend_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class CheckAnswersRequest(BaseModel):
    answers: List[int]
    correct_answers: List[int]

class QuickRevisionRequest(BaseModel):
    text: str

class WeakRevisionRequest(BaseModel):
    weak_topics: List[str]

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi"

def call_ollama(prompt: str, json_mode: bool = False) -> Any:
    """Helper to call local Ollama API."""
    try:
        logging.info(f"Sending request to Ollama ({MODEL_NAME}). JSON Mode: {json_mode}")
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        
        if json_mode:
            payload["format"] = "json"

        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("response", "")
        
        logging.info("Received response from Ollama")
        
        if json_mode:
            try:
                # Phi sometimes wraps JSON in markdown blocks, clean it up
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except json.JSONDecodeError as e:
                logging.error(f"JSON Parse Error: {content}")
                raise HTTPException(status_code=500, detail="Failed to parse valid JSON from AI model.")
        
        return content.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama Connection Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama Error: {str(e)}")
    except Exception as e:
        logging.error(f"General Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
def summarize(request: TextRequest):
    prompt = f"Summarize the following study notes clearly using bullet points and concise language:\n\n{request.text}"
    summary = call_ollama(prompt, json_mode=False)
    return {"summary": summary}

@app.post("/generate-quiz")
def generate_quiz(request: TextRequest):
    prompt = f"""Generate 5 multiple choice questions based on the text below.
Return a valid JSON object with a key "questions" containing a list.
Each question must have: "question", "options" (list of 4 strings), "correct_index" (0-3), and "topic" (string).

Example JSON format:
{{
  "questions": [
    {{ "question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0, "topic": "Concept" }}
  ]
}}

Text:
{request.text}
"""
    data = call_ollama(prompt, json_mode=True)
    # Fallback if AI returns list directly
    if isinstance(data, list):
         return data
    return data.get("questions", [])

@app.post("/check-answers")
def check_answers(request: CheckAnswersRequest):
    score = 0
    if len(request.answers) != len(request.correct_answers):
        return {"score": 0, "total": 0, "error": "Length mismatch"}

    total = len(request.correct_answers)
    for i in range(total):
        if request.answers[i] == request.correct_answers[i]:
            score += 1
            
    return {"score": score, "total": total}

@app.post("/quick-revision")
def quick_revision(request: QuickRevisionRequest):
    prompt = f"""Create a 1-minute revision sheet.
Return valid JSON with keys: "bullets" (list of 5 strings), "tricks" (list of 3 strings), "recap" (string).

Text:
{request.text}
"""
    data = call_ollama(prompt, json_mode=True)
    return data

@app.post("/weak-revision")
def weak_revision(request: WeakRevisionRequest):
    topics = ", ".join(request.weak_topics)
    prompt = f"Provide focused revision guidance for these weak topics: {topics}. Explain clearly and concisely with improvement advice."
    revision_text = call_ollama(prompt, json_mode=False)
    return {"revision_text": revision_text}
