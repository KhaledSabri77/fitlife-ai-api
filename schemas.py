from pydantic import BaseModel, Field
from typing import Dict, Any, List


class UserInput(BaseModel):
        age: int
        gender: str
        height: float
        weight: float
        fitnessGoal: str
        activityLevel: str
        experienceLevel: str
        workoutLocation: str
        workoutDays: int


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
        workout_plan: Dict[str, List[Dict[str, Any]]]
