from pydantic import BaseModel, Field
from typing import List, Dict, Any



class UserInput(BaseModel):
    age: int
    gender: str
    height: float
    weight: float

    fitnessGoal: str
    workout_days: int
    equipment: str


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
