from pydantic import BaseModel
from typing import List, Dict, Any



class UserInput(BaseModel):
    age: int = Field(..., ge=10, le=120, description="User age in years")
    gender: str = Field(..., description="User gender")
    weight: float = Field(..., gt=0, description="Weight in kg")
    height: float = Field(..., gt=0, description="Height in meters")
    goal: str = Field(..., description="Fitness goal (e.g., lose_weight, gain_muscle, maintain)")
    workout_days: int = Field(..., ge=1, le=7, description="Number of workout days per week")
    level: str = Field(..., description="Fitness level (beginner, intermediate, advanced)")
    equipment: str = Field(..., description="Available equipment (none, minimal, full_gym)")
    dietary_preference: str = Field(..., description="Dietary preference (standard, vegetarian, vegan, keto)")


class ExerciseItem(BaseModel):
    Exercise_Name: str = Field(..., alias="Exercise Name")
    Execution: str
    Main_muscle: str
    Target_Muscles: str
    Sets: str
    Reps_per_Set: str = Field(..., alias="Reps per Set")

    class Config:
        populate_by_name = True


class DietPlan(BaseModel):
    daily_calorie_target: str
    Breakfast_Suggestion: List[str] = Field(..., alias="Breakfast Suggestion")
    Lunch_Suggestion: List[str] = Field(..., alias="Lunch Suggestion")
    Dinner_Suggestion: List[str] = Field(..., alias="Dinner Suggestion")
    Snack_Suggestion: List[str] = Field(..., alias="Snack Suggestion")

    class Config:
        populate_by_name = True


class PlanResponse(BaseModel):
    bmi: float
    bmi_category: str
    daily_calorie_target: float
    recommendations: str
    workout_plan: List[Dict[str, Any]]
    diet_plan: Dict[str, Any]
