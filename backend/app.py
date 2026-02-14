import requests
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SATWA backend running"}

@app.get("/joke")
def get_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    data = response.json()

    return {
        "setup": data["setup"],
        "punchline": data["punchline"]
    }
