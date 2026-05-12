"""
main.py - FitLife AI Smart Workout Planner.
Generates intelligent, day-grouped workout plans based on BMI and user profile.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserInput, PlanResponse
from services import generate_plan


app = FastAPI(
    title="FitLife AI - Smart Workout Planner",
    description="Generate personalized workout plans based on BMI, fitness goals, experience level, and workout location.",
    version="4.0.0",
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
        "message": "FitLife AI Smart Workout Planner is running",
        "version": "4.0.0",
        "endpoints": {
            "health": "/health",
            "generate_plan": "/generate-plan",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-plan", response_model=PlanResponse, tags=["Plan"])
async def create_plan(user: UserInput):
    try:
        return generate_plan(user)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
