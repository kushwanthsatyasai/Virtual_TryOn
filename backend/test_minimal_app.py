"""
Minimal FastAPI app to test if server can start
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
@app.get("/health")
def health():
    return {"status": "healthy", "message": "Server is running"}
