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
    weight: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    goal: str
    workout_days: int = Field(..., ge=1, le=7)
    level: str
    equipment: str
    dietary_preference: str


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
    bmi: float
    bmi_category: str
    daily_calorie_target: int
    recommendations: str
    workout_plan: List[dict]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BMI Logic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bmi(weight: float, height: float) -> float:
    return round(weight / (height ** 2), 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5: return "Underweight"
    elif bmi < 25.0: return "Normal"
    elif bmi < 30.0: return "Overweight"
    return "Obese"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Calorie Logic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_calories(user: UserInput) -> int:
    if user.gender.lower() in ("male", "m"):
        bmr = 10 * user.weight + 6.25 * (user.height * 100) - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * (user.height * 100) - 5 * user.age - 161
    activity = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.725, 6: 1.725, 7: 1.9}
    tdee = bmr * activity.get(user.workout_days, 1.55)
    goal = user.goal.lower().replace(" ", "_")
    if goal in ("lose_weight", "fat_loss", "cut"):
        return max(1800, min(2200, int(tdee - 500)))
    elif goal in ("gain_muscle", "bulk", "muscle_gain"):
        return max(2200, min(2800, int(tdee + 300)))
    return max(1800, min(2200, int(tdee)))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Recommendations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_recommendations(bmi_cat: str, goal: str, days: int) -> str:
    parts = []
    if bmi_cat == "Underweight":
        parts.append("Your BMI indicates you are underweight. Focus on calorie-surplus meals with adequate protein.")
    elif bmi_cat in ("Overweight", "Obese"):
        parts.append(f"Your BMI falls in the {bmi_cat} range. Prioritize a moderate calorie deficit with high-protein foods.")
    else:
        parts.append("Your BMI is in the normal range. Maintain a balanced diet aligned with your goal.")
    g = goal.lower().replace(" ", "_")
    if g in ("lose_weight", "fat_loss", "cut"):
        parts.append(f"For fat loss with {days} training days, include cardio and resistance training.")
    elif g in ("gain_muscle", "bulk", "muscle_gain"):
        parts.append(f"For muscle gain with {days} training days, emphasize progressive overload and compound lifts.")
    else:
        parts.append(f"With {days} training days, combine strength and cardio for overall fitness.")
    if days <= 2:
        parts.append("Consider adding an extra day for active recovery like walking or yoga.")
    elif days >= 6:
        parts.append("Ensure at least one full rest day per week for recovery.")
    return " ".join(parts)


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
    split = SPLITS.get(user.workout_days, SPLITS[3])
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
    if user.level.lower() == "beginner":
        for ex in result:
            ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orchestrator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_plan(user: UserInput) -> dict:
    bmi = calculate_bmi(user.weight, user.height)
    bmi_cat = classify_bmi(bmi)
    cal = calculate_calories(user)
    recs = build_recommendations(bmi_cat, user.goal, user.workout_days)
    workout = build_workout(user)
    return {
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "daily_calorie_target": cal,
        "recommendations": recs,
        "workout_plan": workout,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI App
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="AI Fitness Workout Planner",
    description="Generate personalized workout plans based on your profile.",
    version="3.0.0",
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
