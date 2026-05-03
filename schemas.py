from pydantic import BaseModel, Field
from typing import List, Dict, Any



class UserInput(BaseModel):
   age: int = Field(..., ge=10, le=120, description="User age in years")
gender: str = Field(..., description="User gender")
height: float = Field(..., gt=0, description="Height in meters")
weight: float = Field(..., gt=0, description="Weight in kg")
fitnessGoal: str = Field(..., description="Fitness goal (muscle gain, fat loss, maintenance)")
activityLevel: str = Field(..., description="Activity level (low, moderate, high)")
experienceLevel: str = Field(..., description="Experience level (beginner, intermediate, advanced)")
workoutLocation: str = Field(..., description="Workout location (home, gym)")
workoutDays: int = Field(..., ge=1, le=7, description="Workout days per week")


class ExerciseItem(BaseModel):
    Exercise_Name: str = Field(..., alias="Exercise Name")
    Execution: str
    Main_muscle: str
    Target_Muscles: str
    Sets: str
    Reps_per_Set: str = Field(..., alias="Reps per Set")

    class Config:
        populate_by_name = True


class PlanResponse(BaseModel):
    bmi: float
    bmi_category: str
    daily_calorie_target: float
    recommendations: str
    workout_plan: List[Dict[str, Any]]
