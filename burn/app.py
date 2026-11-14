"""Web app entry point. Run: uv run uvicorn burn.app:app --reload"""
from fastapi import FastAPI

app = FastAPI(title="Harmonized Burning Activity Calendar")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
