"""
main.py – FastAPI application for the FitLife AI Fitness & Nutrition Planner.
Deployed on Koyeb (free tier).
"""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import UserInput, PlanResponse
from services import generate_plan

app = FastAPI(
    title="AI Fitness & Nutrition Planner",
    description="Generate personalized workout and diet plans based on your profile.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Fitness & Nutrition Planner API",
        "version": "1.0.0",
        "endpoints": {
            "generate_plan": "/generate-plan",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-plan", response_model=PlanResponse, tags=["Plan"])
async def create_plan(user: UserInput):
    try:
        result = generate_plan(user)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
