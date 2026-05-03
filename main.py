"""
main.py - FitLife AI Fitness Planner API.

Thin FastAPI layer: validation, routing, and error handling only.
All business logic lives in services.py.
"""

import os
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import PlanResponse, UserInput
from services import generate_plan


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Application Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="FitLife AI Fitness Planner",
    description=(
        "Generate personalized workout plans, BMI analysis, "
        "calorie targets, and actionable recommendations."
    ),
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Health & Root
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@app.get("/", tags=["Root"], summary="API status check")
async def root():
    """Return a simple health message confirming the API is live."""
    return {
        "status": "online",
        "service": "FitLife AI Fitness Planner",
        "version": "5.0.0",
    }


@app.get("/health", tags=["Health"], summary="Health probe")
async def health_check():
    """Liveness probe for container orchestrators (K8s, ECS, etc.)."""
    return {"status": "healthy"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Plan Generation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@app.post(
    "/generate-plan",
    response_model=PlanResponse,
    tags=["Plan"],
    summary="Generate a personalized fitness plan",
    status_code=status.HTTP_200_OK,
)
async def create_plan(user: UserInput):
    """Accept user profile and return a complete fitness plan.

    The response includes:
    - **bmi**: BMI value and WHO classification
    - **nutrition**: daily calorie target
    - **recommendations**: structured, category-tagged advice
    - **workout_plan**: day-grouped exercises with sets/reps

    Raises:
        422: Validation error (invalid input).
        500: Unexpected server error.
    """
    try:
        result = generate_plan(user)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plan generation failed: {str(exc)}",
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Entrypoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
