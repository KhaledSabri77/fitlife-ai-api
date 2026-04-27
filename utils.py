"""
utils.py – Helper functions for BMI, calorie targets, macros, and feature vectorisation.

All calculations are goal-aware and follow evidence-based formulas
(Mifflin-St Jeor for BMR, WHO for BMI classification).
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Encoding maps (used by both utils and model)
# ---------------------------------------------------------------------------

GOAL_ENCODING: dict[str, int] = {"fat loss": 0, "maintenance": 1, "muscle gain": 2}
LEVEL_ENCODING: dict[str, int] = {"beginner": 0, "intermediate": 1, "advanced": 2}
GENDER_ENCODING: dict[str, float] = {"male": 1.0, "m": 1.0, "female": 0.0, "f": 0.0}

ACTIVITY_MULTIPLIER: dict[int, float] = {
    1: 1.2,
    2: 1.2,
    3: 1.375,
    4: 1.375,
    5: 1.55,
    6: 1.725,
    7: 1.9,
}

GOAL_ADJUSTMENT: dict[str, int] = {
    "fat loss": -500,
    "muscle gain": +300,
    "maintenance": 0,
}


# ---------------------------------------------------------------------------
# BMI
# ---------------------------------------------------------------------------

def calculate_bmi(weight_kg: float, height_m: float) -> tuple[float, str]:
    """Return (bmi_value, bmi_category)."""
    bmi = round(weight_kg / (height_m ** 2), 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


# ---------------------------------------------------------------------------
# Daily calorie target (Mifflin-St Jeor + activity/goal)
# ---------------------------------------------------------------------------

def calculate_daily_calories(
    age: int,
    gender: str,
    weight_kg: float,
    height_m: float,
    workout_days: int,
    goal: str,
) -> int:
    """Return daily calorie target as an integer."""
    height_cm = height_m * 100

    # Mifflin-St Jeor BMR
    if gender.lower() in ("male", "m"):
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity = ACTIVITY_MULTIPLIER.get(workout_days, 1.375)
    tdee = bmr * activity
    adjustment = GOAL_ADJUSTMENT.get(goal.lower(), 0)
    return int(round(tdee + adjustment))


# ---------------------------------------------------------------------------
# Recommendation text generator
# ---------------------------------------------------------------------------

def build_recommendations(
    bmi_category: str,
    goal: str,
    daily_calories: int,
    level: str,
) -> str:
    """Return a brief, data-driven recommendation string."""
    recs: list[str] = []

    # BMI-based advice
    bmi_advice = {
        "Underweight": (
            "Your BMI indicates you are underweight. "
            "Focus on a caloric surplus with nutrient-dense foods."
        ),
        "Normal weight": (
            "Your BMI is in the healthy range. "
            "Maintain balance between training and recovery."
        ),
        "Overweight": (
            "Your BMI indicates you are overweight. "
            "Combining cardio with resistance training will be most effective."
        ),
        "Obese": (
            "Your BMI indicates obesity. Prioritise low-impact cardio and "
            "progressive resistance work. Consult a healthcare professional before starting."
        ),
    }
    recs.append(bmi_advice.get(bmi_category, ""))

    # Goal-based advice
    goal_advice = {
        "fat loss": (
            f"Your daily calorie target is {daily_calories} kcal (deficit). "
            "Prioritise high-protein meals to preserve muscle mass."
        ),
        "muscle gain": (
            f"Your daily calorie target is {daily_calories} kcal (surplus). "
            "Consume adequate protein (1.6–2.2 g/kg body weight) and "
            "time carbs around workouts."
        ),
        "maintenance": (
            f"Your daily calorie target is {daily_calories} kcal (maintenance). "
            "Keep macros balanced and focus on progressive overload."
        ),
    }
    recs.append(goal_advice.get(goal.lower(), f"Target {daily_calories} kcal/day."))

    # Level-based advice
    level_advice = {
        "beginner": (
            "As a beginner, focus on mastering form before increasing load. "
            "Rest 60–90 s between sets."
        ),
        "intermediate": (
            "At intermediate level, apply progressive overload weekly. "
            "Rest 60–120 s between sets."
        ),
        "advanced": (
            "As an advanced athlete, incorporate periodisation and deload weeks. "
            "Rest 120–180 s between sets."
        ),
    }
    recs.append(level_advice.get(level.lower(), ""))

    return " ".join(filter(None, recs))


# ---------------------------------------------------------------------------
# Macro split helpers
# ---------------------------------------------------------------------------

def split_macros(calories: int, goal: str) -> dict[str, int]:
    """Return protein/carb/fat grams for a given calorie total and goal."""
    goal = goal.lower()
    if goal == "fat loss":
        p_pct, c_pct, f_pct = 0.40, 0.30, 0.30
    elif goal == "muscle gain":
        p_pct, c_pct, f_pct = 0.30, 0.50, 0.20
    else:  # maintenance
        p_pct, c_pct, f_pct = 0.30, 0.40, 0.30

    protein_g = int(round(calories * p_pct / 4))
    carbs_g = int(round(calories * c_pct / 4))
    fat_g = int(round(calories * f_pct / 9))
    return {"protein": protein_g, "carbohydrates": carbs_g, "fat": fat_g}


# ---------------------------------------------------------------------------
# Feature vectorisation for cosine similarity
# ---------------------------------------------------------------------------

def user_to_vector(
    age: int,
    gender: str,
    weight_kg: float,
    height_m: float,
    goal: str,
    workout_days: int,
    level: str,
) -> np.ndarray:
    """Convert user profile to a numeric vector for similarity matching."""
    bmi = weight_kg / (height_m ** 2)
    return np.array(
        [
            age / 80.0,
            GENDER_ENCODING.get(gender.lower(), 0),
            bmi / 40.0,
            GOAL_ENCODING.get(goal.lower(), 1) / 2.0,
            workout_days / 7.0,
            LEVEL_ENCODING.get(level.lower(), 0) / 2.0,
        ],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# Difficulty ↔ Level mapping
# ---------------------------------------------------------------------------

def difficulty_to_level(difficulty: int) -> str:
    """Map a 1-5 difficulty score to a level string."""
    if difficulty <= 2:
        return "beginner"
    elif difficulty <= 3:
        return "intermediate"
    else:
        return "advanced"


def level_to_difficulty_range(level: str) -> tuple[int, int]:
    """Map a level string to a (min, max) difficulty range."""
    level = level.lower()
    if level == "beginner":
        return (1, 2)
    elif level == "intermediate":
        return (2, 4)
    else:  # advanced
        return (3, 5)


# ---------------------------------------------------------------------------
# Goal ↔ Activity Level mapping for nutrition matching
# ---------------------------------------------------------------------------

GOAL_TO_ACTIVITY: dict[str, list[str]] = {
    "fat loss": ["sedentary", "lightly active", "moderately active"],
    "maintenance": ["moderately active", "active"],
    "muscle gain": ["active", "very active", "moderately active"],
}
