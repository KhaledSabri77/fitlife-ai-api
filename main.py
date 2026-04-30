"""
main.py - FitLife AI Fitness & Nutrition Planner (fully self-contained).
All logic inline - no placeholder values.
"""
import os
from typing import List, Optional

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


class MealItem(BaseModel):
    name: str
    calories: int
    protein: int
    carbohydrates: int
    fat: int


class DietPlan(BaseModel):
    daily_calorie_target: int
    Breakfast_Suggestion: List[MealItem] = Field(alias="Breakfast Suggestion")
    Lunch_Suggestion: List[MealItem] = Field(alias="Lunch Suggestion")
    Dinner_Suggestion: List[MealItem] = Field(alias="Dinner Suggestion")
    Snack_Suggestion: List[MealItem] = Field(alias="Snack Suggestion")
    class Config:
        populate_by_name = True


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
    diet_plan: dict


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BMI Logic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bmi(weight: float, height: float) -> float:
    return round(weight / (height ** 2), 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
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
    if user.level.lower() == "beginner":
        for ex in result:
            ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Diet Plan (with macros)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MEALS = {
    "standard": {
        "Breakfast Suggestion": [
            {"name": "Scrambled eggs with whole-grain toast", "calories": 420, "protein": 28, "carbohydrates": 35, "fat": 18},
            {"name": "Greek yogurt with granola and berries", "calories": 350, "protein": 22, "carbohydrates": 45, "fat": 10},
            {"name": "Oatmeal with banana and peanut butter", "calories": 450, "protein": 15, "carbohydrates": 60, "fat": 16},
        ],
        "Lunch Suggestion": [
            {"name": "Grilled chicken with brown rice and broccoli", "calories": 550, "protein": 42, "carbohydrates": 55, "fat": 14},
            {"name": "Turkey avocado wrap with side salad", "calories": 520, "protein": 35, "carbohydrates": 40, "fat": 22},
            {"name": "Salmon with quinoa and roasted vegetables", "calories": 580, "protein": 38, "carbohydrates": 48, "fat": 20},
        ],
        "Dinner Suggestion": [
            {"name": "Lean steak with sweet potato and asparagus", "calories": 600, "protein": 45, "carbohydrates": 50, "fat": 18},
            {"name": "Baked chicken thighs with mixed vegetables", "calories": 520, "protein": 40, "carbohydrates": 35, "fat": 20},
            {"name": "Shrimp stir-fry with brown rice", "calories": 480, "protein": 32, "carbohydrates": 55, "fat": 12},
        ],
        "Snack Suggestion": [
            {"name": "Mixed nuts and dried fruit", "calories": 280, "protein": 8, "carbohydrates": 30, "fat": 16},
            {"name": "Protein shake with banana", "calories": 320, "protein": 30, "carbohydrates": 35, "fat": 5},
            {"name": "Apple slices with almond butter", "calories": 250, "protein": 6, "carbohydrates": 28, "fat": 14},
        ],
    },
    "vegetarian": {
        "Breakfast Suggestion": [
            {"name": "Veggie omelette with cheese and toast", "calories": 400, "protein": 24, "carbohydrates": 30, "fat": 20},
            {"name": "Smoothie bowl with berries and seeds", "calories": 380, "protein": 14, "carbohydrates": 55, "fat": 12},
        ],
        "Lunch Suggestion": [
            {"name": "Chickpea curry with brown rice", "calories": 520, "protein": 22, "carbohydrates": 70, "fat": 14},
            {"name": "Black bean quesadilla with guacamole", "calories": 560, "protein": 24, "carbohydrates": 55, "fat": 26},
        ],
        "Dinner Suggestion": [
            {"name": "Stuffed bell peppers with rice and beans", "calories": 480, "protein": 20, "carbohydrates": 60, "fat": 14},
            {"name": "Tofu stir-fry with noodles", "calories": 500, "protein": 28, "carbohydrates": 55, "fat": 16},
        ],
        "Snack Suggestion": [
            {"name": "Hummus with carrot and celery sticks", "calories": 220, "protein": 8, "carbohydrates": 24, "fat": 12},
            {"name": "Cottage cheese with pineapple", "calories": 200, "protein": 18, "carbohydrates": 22, "fat": 4},
        ],
    },
    "vegan": {
        "Breakfast Suggestion": [
            {"name": "Chia pudding with coconut milk and mango", "calories": 360, "protein": 10, "carbohydrates": 45, "fat": 16},
            {"name": "Avocado toast with cherry tomatoes", "calories": 380, "protein": 10, "carbohydrates": 38, "fat": 22},
        ],
        "Lunch Suggestion": [
            {"name": "Lentil soup with crusty bread", "calories": 480, "protein": 24, "carbohydrates": 65, "fat": 10},
            {"name": "Buddha bowl with chickpeas and tahini", "calories": 540, "protein": 20, "carbohydrates": 60, "fat": 22},
        ],
        "Dinner Suggestion": [
            {"name": "Tofu stir-fry with brown rice", "calories": 500, "protein": 26, "carbohydrates": 58, "fat": 16},
            {"name": "Stuffed sweet potatoes with black beans", "calories": 460, "protein": 18, "carbohydrates": 65, "fat": 12},
        ],
        "Snack Suggestion": [
            {"name": "Edamame with sea salt", "calories": 190, "protein": 17, "carbohydrates": 14, "fat": 8},
            {"name": "Energy balls with oats and dates", "calories": 240, "protein": 6, "carbohydrates": 36, "fat": 10},
        ],
    },
    "keto": {
        "Breakfast Suggestion": [
            {"name": "Bacon and eggs with avocado", "calories": 520, "protein": 30, "carbohydrates": 6, "fat": 42},
            {"name": "Keto smoothie with MCT oil and spinach", "calories": 400, "protein": 20, "carbohydrates": 8, "fat": 32},
        ],
        "Lunch Suggestion": [
            {"name": "Grilled chicken Caesar salad (no croutons)", "calories": 480, "protein": 40, "carbohydrates": 8, "fat": 32},
            {"name": "Bunless cheeseburger lettuce wrap", "calories": 520, "protein": 38, "carbohydrates": 6, "fat": 38},
        ],
        "Dinner Suggestion": [
            {"name": "Salmon with butter-sauteed asparagus", "calories": 560, "protein": 42, "carbohydrates": 8, "fat": 40},
            {"name": "Pork chops with creamed spinach", "calories": 580, "protein": 40, "carbohydrates": 10, "fat": 42},
        ],
        "Snack Suggestion": [
            {"name": "Cheese crisps", "calories": 180, "protein": 12, "carbohydrates": 2, "fat": 14},
            {"name": "Handful of macadamia nuts", "calories": 240, "protein": 4, "carbohydrates": 4, "fat": 24},
        ],
    },
}


def build_diet(user: UserInput, daily_cal: int) -> dict:
    pref = user.dietary_preference.lower().strip()
    meals = MEALS.get(pref, MEALS["standard"])
    return {
        "daily_calorie_target": daily_cal,
        "Breakfast Suggestion": meals["Breakfast Suggestion"],
        "Lunch Suggestion": meals["Lunch Suggestion"],
        "Dinner Suggestion": meals["Dinner Suggestion"],
        "Snack Suggestion": meals["Snack Suggestion"],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orchestrator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_plan(user: UserInput) -> dict:
    bmi = calculate_bmi(user.weight, user.height)
    bmi_cat = classify_bmi(bmi)
    cal = calculate_calories(user)
    recs = build_recommendations(bmi_cat, user.goal, user.workout_days)
    workout = build_workout(user)
    diet = build_diet(user, cal)
    return {
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "daily_calorie_target": cal,
        "recommendations": recs,
        "workout_plan": workout,
        "diet_plan": diet,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI App
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="AI Fitness & Nutrition Planner",
    description="Generate personalized workout and diet plans based on your profile.",
    version="2.0.0",
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
