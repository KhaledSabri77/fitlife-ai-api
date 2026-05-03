"""
schemas.py - Pydantic models for FitLife AI Fitness Planner.

Defines request/response contracts for the API. All models use
strict validation to reject malformed input at the boundary.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums — single source of truth for valid option values
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class Gender(str, Enum):
    """Biological gender used for BMR calculation."""
    MALE = "male"
    FEMALE = "female"


class FitnessGoal(str, Enum):
    """User's primary fitness objective."""
    LOSE_WEIGHT = "lose_weight"
    GAIN_MUSCLE = "gain_muscle"
    MAINTAIN = "maintain"


class ExperienceLevel(str, Enum):
    """Training experience tier."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WorkoutLocation(str, Enum):
    """Available training environment / equipment access."""
    HOME = "home"
    GYM = "gym"
    OUTDOOR = "outdoor"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Request Model
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UserInput(BaseModel):
    """Incoming user profile for plan generation."""

    age: int = Field(..., ge=10, le=120, description="User age in years")
    gender: Gender = Field(..., description="Biological gender (male / female)")
    height: float = Field(..., gt=0, description="Height in meters")
    weight: float = Field(..., gt=0, description="Weight in kg")
    fitnessGoal: FitnessGoal = Field(
        ..., description="Primary fitness goal"
    )
    activityLevel: str = Field(
        ..., description="General daily activity (sedentary, light, moderate, active, very_active)"
    )
    experienceLevel: ExperienceLevel = Field(
        ..., description="Training experience level"
    )
    workoutLocation: WorkoutLocation = Field(
        ..., description="Where the user trains"
    )
    workoutDays: int = Field(
        ..., ge=1, le=7, description="Training days per week"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Response Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ExerciseItem(BaseModel):
    """Single exercise within a workout day."""

    exercise_name: str = Field(..., alias="Exercise Name")
    execution: str = Field(..., alias="Execution")
    main_muscle: str = Field(..., alias="Main_muscle")
    target_muscles: str = Field(..., alias="Target_Muscles")
    sets: str = Field(..., alias="Sets")
    reps_per_set: str = Field(..., alias="Reps per Set")

    class Config:
        populate_by_name = True


class WorkoutDay(BaseModel):
    """A single training day with its target muscles and exercises."""

    day: str = Field(..., description="Day label, e.g. 'Day 1'")
    muscles: List[str] = Field(..., description="Muscle groups targeted")
    exercises: List[Dict] = Field(..., description="Exercises for this day")


class RecommendationItem(BaseModel):
    """One structured recommendation entry."""

    category: str = Field(..., description="Recommendation category")
    message: str = Field(..., description="Actionable advice")


class BMIResult(BaseModel):
    """BMI calculation result."""

    value: float = Field(..., description="Calculated BMI value")
    category: str = Field(..., description="BMI classification")


class NutritionResult(BaseModel):
    """Daily calorie target."""

    daily_calorie_target: int = Field(..., description="Estimated daily calories")


class PlanResponse(BaseModel):
    """Full plan returned by POST /generate-plan."""

    bmi: BMIResult
    nutrition: NutritionResult
    recommendations: List[RecommendationItem]
    workout_plan: List[WorkoutDay]
