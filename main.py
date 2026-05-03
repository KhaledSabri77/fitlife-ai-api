"""
main.py - FitLife AI Workout Planner (fully self-contained).
All logic inline - no placeholder values.
"""
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class UserInput(BaseModel):
    age: int = Field(..., ge=10, le=120)
    gender: str
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    fitnessGoal: str
    activityLevel: str
    experienceLevel: str
    workoutLocation: str
    workoutDays: int = Field(..., ge=1, le=7)


class ExerciseItem(BaseModel):
    Exercise_Name: str = Field(alias="Exercise Name")
    Execution: str
    Main_muscle: str
    Target_Muscles: str
    Sets: str
    Reps_per_Set: str = Field(alias="Reps per Set")
    class Config:
        populate_by_name = True


class PlanResponse(BaseModel):
    workout_plan: List[dict]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Workout Plan
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXERCISES = {
    "chest": [
        {"Exercise Name": "Barbell Bench Press", "Execution": "Lie flat, lower bar to chest, press up explosively", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Anterior Deltoids", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Push-Ups", "Execution": "Plank position, lower chest to floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Dumbbell Flyes", "Execution": "Lie on bench, open arms wide with dumbbells, squeeze together", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "back": [
        {"Exercise Name": "Pull-Ups", "Execution": "Overhand grip on bar, pull chin above bar", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps, Rhomboids", "Sets": "4", "Reps per Set": "6-10"},
        {"Exercise Name": "Barbell Rows", "Execution": "Bend over, pull barbell to lower chest, squeeze shoulder blades", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Biceps", "Sets": "4", "Reps per Set": "8-12"},
    ],
    "legs": [
        {"Exercise Name": "Barbell Squat", "Execution": "Bar on upper back, squat to parallel, drive up", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Romanian Deadlift", "Execution": "Hinge at hips with barbell, lower along legs, squeeze glutes up", "Main_muscle": "Legs", "Target_Muscles": "Hamstrings, Glutes, Lower Back", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Walking Lunges", "Execution": "Step forward into lunge, alternate legs", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "12 each leg"},
    ],
    "shoulders": [
        {"Exercise Name": "Overhead Press", "Execution": "Press barbell from shoulders to overhead", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps, Upper Chest", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Lateral Raises", "Execution": "Raise dumbbells to shoulder height out to sides", "Main_muscle": "Shoulders", "Target_Muscles": "Lateral Deltoids", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "arms": [
        {"Exercise Name": "Barbell Curl", "Execution": "Curl barbell to shoulders keeping elbows fixed", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Brachialis", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Tricep Dips", "Execution": "Lower body on parallel bars, press back up", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest, Anterior Deltoids", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "core": [
        {"Exercise Name": "Plank", "Execution": "Hold forearm plank keeping body straight", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 sec"},
        {"Exercise Name": "Hanging Leg Raises", "Execution": "Hang from bar, raise legs to 90 degrees", "Main_muscle": "Core", "Target_Muscles": "Lower Abs, Hip Flexors", "Sets": "3", "Reps per Set": "10-15"},
    ],
}

SPLITS = {
    1: [["chest", "back", "legs"]],
    2: [["chest", "back", "shoulders"], ["legs", "arms", "core"]],
    3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
    4: [["chest", "shoulders"], ["back"], ["legs"], ["arms", "core"]],
    5: [["chest"], ["back"], ["legs"], ["shoulders", "arms"], ["core"]],
    6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"]],
    7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["chest", "back"]],
}


def build_workout(user: UserInput) -> list:
    split = SPLITS.get(user.workoutDays, SPLITS[3])
    result = []
    for day_groups in split:
        for group in day_groups:
            for ex in EXERCISES.get(group, [])[:2]:
                result.append(ex)
    # Guarantee at least 4 exercises
    if len(result) < 4:
        for ex in EXERCISES.get("legs", []) + EXERCISES.get("core", []):
            if ex not in result:
                result.append(ex)
            if len(result) >= 4:
                break
    if user.experienceLevel.lower() == "beginner":
        for ex in result:
            ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orchestrator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_plan(user: UserInput) -> dict:
    workout = build_workout(user)
    return {
        "workout_plan": workout,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI App
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="AI Fitness Workout Planner",
    description="Generate personalized workout plans based on your profile.",
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
    return {"message": "API is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-plan", response_model=PlanResponse, tags=["Plan"])
async def create_plan(user: UserInput):
    try:
        return generate_plan(user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
