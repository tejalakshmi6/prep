from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SATWA 2026 Prep Running"}
