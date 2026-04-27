"""
main.py – FastAPI application for the FitLife AI Fitness & Nutrition Planner.
Deployed on Render with bundled Kaggle datasets.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from model import generate_plan
from utils import calculate_bmi as _bmi
from data_loader import get_dataset_info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("fitlife")

app = FastAPI(
    title="FitLife AI – Fitness & Nutrition Planner",
    description=(
        "Personalised workout and diet plans generated from real Kaggle datasets "
        "using cosine-similarity matching and data-driven meal recommendations.\n\n"
        "**Datasets:**\n"
        "- Gym Exercises: rishitmurarka/gym-exercises-dataset (617 exercises)\n"
        "- Nutrition: bitanianielsen/nutrition-daily-meals-in-diseases-cases (1698 meal plans)\n\n"
        "No fake exercises or random meals – every recommendation comes from real data."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age in years")
    gender: str = Field(..., description="male / female")
    weight: float = Field(..., gt=20, lt=300, description="Body weight in kg")
    height: float = Field(..., gt=0.5, lt=2.7, description="Height in metres")
    goal: str = Field(..., description="fat loss | muscle gain | maintenance")
    workout_days: int = Field(..., ge=1, le=7, description="Training days per week")
    level: str = Field(..., description="beginner | intermediate | advanced")
    equipment: str = Field(default="body weight", description="Available equipment")
    dietary_preference: str = Field(default="omnivore", description="omnivore | vegetarian | vegan | any")

    @field_validator("gender")
    @classmethod
    def _validate_gender(cls, v: str) -> str:
        allowed = {"male", "m", "female", "f"}
        if v.lower() not in allowed:
            raise ValueError(f"gender must be one of {allowed}")
        return v.lower()

    @field_validator("goal")
    @classmethod
    def _validate_goal(cls, v: str) -> str:
        allowed = {"fat loss", "muscle gain", "maintenance"}
        if v.lower() not in allowed:
            raise ValueError(f"goal must be one of {allowed}")
        return v.lower()

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced"}
        if v.lower() not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return v.lower()

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "age": 22,
                "gender": "male",
                "weight": 75.0,
                "height": 1.75,
                "goal": "muscle gain",
                "workout_days": 4,
                "level": "beginner",
                "equipment": "home",
                "dietary_preference": "none",
            }
        },
    }


class BMIRequest(BaseModel):
    weight: float = Field(..., gt=20, lt=300)
    height: float = Field(..., gt=0.5, lt=2.7)


@app.get("/", tags=["System"])
def root():
    return {
        "service": "FitLife AI – Fitness & Nutrition Planner",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": ["/generate-plan", "/bmi", "/health", "/dataset-info"],
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "FitLife AI Planner v2.0"}


@app.get("/dataset-info", tags=["System"])
def dataset_info():
    try:
        return get_dataset_info()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/bmi", tags=["BMI"])
def bmi_endpoint(req: BMIRequest):
    bmi_val, bmi_cat = _bmi(req.weight, req.height)
    return {"bmi": str(bmi_val), "bmi_category": bmi_cat}


@app.post("/generate-plan", tags=["Planner"])
def generate_plan_endpoint(req: PlanRequest):
    logger.info(
        "Plan request: age=%d gender=%s weight=%.1f height=%.2f goal=%s "
        "days=%d level=%s equip=%s diet=%s",
        req.age, req.gender, req.weight, req.height,
        req.goal, req.workout_days, req.level, req.equipment,
        req.dietary_preference,
    )
    try:
        result = generate_plan(
            age=req.age,
            gender=req.gender,
            weight_kg=req.weight,
            height_m=req.height,
            goal=req.goal,
            workout_days=req.workout_days,
            level=req.level,
            equipment=req.equipment,
            dietary_preference=req.dietary_preference,
        )
        return result
    except FileNotFoundError as exc:
        logger.error("Dataset missing: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /generate-plan")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


@app.post("/plan", tags=["Planner"], include_in_schema=False)
def plan_endpoint(req: PlanRequest):
    return generate_plan_endpoint(req)
