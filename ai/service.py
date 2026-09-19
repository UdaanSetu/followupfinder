"""CPU-first HTTP service for FollowUpFinder AI extraction."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from ai.inference import extract_followup
from ai.inference.model_loader import load_model


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model before serving requests and release it on shutdown."""
    _, _, device = load_model()
    app.state.model_loaded = True
    app.state.device = str(device)
    try:
        yield
    finally:
        app.state.model_loaded = False
        app.state.device = None


app = FastAPI(title="FollowUpFinder AI", lifespan=lifespan)


@app.get("/health")
def health(response: Response) -> dict[str, Any]:
    model_loaded = bool(getattr(app.state, "model_loaded", False))
    if not model_loaded:
        response.status_code = 503
    return {
        "status": "ok" if model_loaded else "starting",
        "model_loaded": model_loaded,
        "device": getattr(app.state, "device", None),
    }


@app.post("/extract")
def extract(request: ExtractRequest) -> dict[str, Any]:
    try:
        return extract_followup(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
