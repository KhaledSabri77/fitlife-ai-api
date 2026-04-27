"""
model.py – Core AI/ML logic for workout recommendation and diet planning.

Workout selection:
  Uses cosine similarity on a feature vector built from the real Kaggle
  gym-exercises dataset.  Every returned exercise is a real row from the CSV.

Diet planning:
  Uses the Kaggle nutrition-daily-meals dataset to find real meal suggestions
  filtered by dietary preference and calorie target.  Falls back to
  intelligent generation when no match is found.
"""
from __future__ import annotations

import logging
import random
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from data_loader import load_workout_dataset, load_nutrition_dataset
from utils import (
    calculate_bmi,
    calculate_daily_calories,
    build_recommendations,
    split_macros,
    GOAL_ENCODING,
    LEVEL_ENCODING,
    GENDER_ENCODING,
    level_to_difficulty_range,
)

logger = logging.getLogger("fitlife.model")

# ---------------------------------------------------------------------------
# Top equipment types for one-hot encoding
# ---------------------------------------------------------------------------
TOP_EQUIPMENT = [
    "barbell", "dumbbell", "body weight", "cable",
    "lever", "smith", "weighted", "band",
]


# ---------------------------------------------------------------------------
# Feature matrix construction (workout)
# ---------------------------------------------------------------------------

def _encode_equipment_vector(equipment_str: str) -> list[float]:
    """One-hot encode equipment against TOP_EQUIPMENT list."""
    eq_lower = str(equipment_str).lower()
    return [1.0 if eq in eq_lower else 0.0 for eq in TOP_EQUIPMENT]


def _build_workout_features(df: pd.DataFrame) -> np.ndarray:
    """
    Build a numeric feature matrix from the workout DataFrame.
    Auto-detects available columns and uses what exists.
    """
    features: list[np.ndarray] = []

    # Difficulty → normalised 0-1
    if "Difficulty" in df.columns:
        diff_vals = pd.to_numeric(df["Difficulty"], errors="coerce").fillna(2.5).values
        features.append((diff_vals / 5.0).reshape(-1, 1))
    else:
        features.append(np.full((len(df), 1), 0.5))

    # Equipment one-hot
    if "Equipment" in df.columns:
        equip_matrix = np.array(
            [_encode_equipment_vector(eq) for eq in df["Equipment"].fillna("body weight")]
        )
        features.append(equip_matrix)
    else:
        features.append(np.zeros((len(df), len(TOP_EQUIPMENT))))

    # Mechanics: compound=1, isolated=0
    if "Mechanics" in df.columns:
        mech = df["Mechanics"].str.lower().fillna("compound")
        features.append((mech == "compound").astype(float).values.reshape(-1, 1))
    else:
        features.append(np.full((len(df), 1), 0.5))

    # Force: push=1, pull=0, both=0.5
    if "Force" in df.columns:
        force_map = {"push": 1.0, "pull": 0.0, "push & pull": 0.5}
        force_vals = df["Force"].str.lower().fillna("push").map(force_map).fillna(0.5).values
        features.append(force_vals.reshape(-1, 1))
    else:
        features.append(np.full((len(df), 1), 0.5))

    X = np.hstack(features)
    scaler = MinMaxScaler()
    return scaler.fit_transform(X)


def _build_user_workout_vector(
    level: str,
    goal: str,
    gender: str,
    equipment: str,
) -> np.ndarray:
    """Build a user feature vector matching the structure of _build_workout_features."""
    # Difficulty based on level
    diff_ranges = level_to_difficulty_range(level)
    diff_norm = np.mean(diff_ranges) / 5.0

    # Equipment one-hot
    equip_vec = _encode_equipment_vector(equipment)

    # Goal → mechanics preference: muscle gain prefers compound, fat loss prefers either
    mechanics_pref = 0.8 if goal.lower() == "muscle gain" else 0.5

    # Goal → force preference
    force_pref = 0.5  # neutral

    vec = [diff_norm] + equip_vec + [mechanics_pref, force_pref]
    return np.array(vec, dtype=float)


# ---------------------------------------------------------------------------
# Workout recommendation engine
# ---------------------------------------------------------------------------

def recommend_exercises(
    goal: str,
    level: str,
    gender: str,
    equipment: str,
    workout_days: int,
    n_exercises: int = 6,
) -> list[dict[str, str]]:
    """
    Return a list of exercise dicts selected from the Kaggle dataset
    via cosine similarity.

    Strategy:
    1. Load dataset with auto-detected columns
    2. Pre-filter by difficulty range and equipment (soft filters)
    3. Compute cosine similarity between user vector and exercise features
    4. Pick top-N with slight random perturbation for variety
    """
    df, _ = load_workout_dataset()
    filtered = df.copy()

    # Soft filter: restrict by difficulty range if column exists
    if "Difficulty" in filtered.columns:
        diff_min, diff_max = level_to_difficulty_range(level)
        difficulty_vals = pd.to_numeric(filtered["Difficulty"], errors="coerce").fillna(3)
        subset = filtered[(difficulty_vals >= diff_min) & (difficulty_vals <= diff_max)]
        if len(subset) >= n_exercises:
            filtered = subset

    # Soft filter: equipment preference
    if "Equipment" in filtered.columns and equipment.strip():
        eq_lower = equipment.lower()
        subset = filtered[
            filtered["Equipment"].str.lower().str.contains(eq_lower, na=False)
        ]
        if len(subset) >= n_exercises:
            filtered = subset

    # Build feature matrix & user vector
    feat_matrix = _build_workout_features(filtered)
    user_vec = _build_user_workout_vector(level, goal, gender, equipment)

    # Align dimensions
    if user_vec.shape[0] != feat_matrix.shape[1]:
        min_len = min(user_vec.shape[0], feat_matrix.shape[1])
        user_vec = user_vec[:min_len]
        feat_matrix = feat_matrix[:, :min_len]

    # Cosine similarity with noise for variety
    sims = cosine_similarity(user_vec.reshape(1, -1), feat_matrix)[0]
    noise = np.random.uniform(0, 0.05, size=sims.shape)
    sims = sims + noise

    # Ensure we get diverse muscle groups
    top_n = min(n_exercises * 3, len(filtered))
    top_indices = np.argsort(sims)[::-1][:top_n]
    candidates = filtered.iloc[top_indices]

    # Diversify by Main_muscle
    selected_indices: list[int] = []
    seen_muscles: set[str] = set()

    for idx in top_indices:
        if len(selected_indices) >= n_exercises:
            break
        row = filtered.iloc[idx]
        muscle = str(row.get("Main_muscle", "")).strip().lower()
        # Allow up to 2 exercises per muscle group
        muscle_count = sum(1 for i in selected_indices
                          if str(filtered.iloc[i].get("Main_muscle", "")).strip().lower() == muscle)
        if muscle_count < 2:
            selected_indices.append(idx)

    # If we still need more, fill without diversity constraint
    if len(selected_indices) < n_exercises:
        for idx in top_indices:
            if idx not in selected_indices:
                selected_indices.append(idx)
            if len(selected_indices) >= n_exercises:
                break

    selected = filtered.iloc[selected_indices[:n_exercises]]

    # Build output with Sets/Reps based on goal
    sets_reps = _goal_sets_reps(goal, level)

    exercises = []
    for _, row in selected.iterrows():
        ex_name = str(row.get("Exercise Name", "")).strip()
        execution = str(row.get("Execution", "")).strip()
        if not execution or execution == "nan":
            prep = str(row.get("Preparation", "")).strip()
            execution = prep if prep and prep != "nan" else f"Perform {ex_name} with controlled form."

        exercises.append({
            "Exercise Name": ex_name,
            "Execution": execution,
            "Main_muscle": str(row.get("Main_muscle", "Full Body")).strip(),
            "Target_Muscles": str(row.get("Target_Muscles", "")).strip().rstrip(",").strip(),
            "Sets": sets_reps["sets"],
            "Reps per Set": sets_reps["reps"],
        })

    return exercises


def _goal_sets_reps(goal: str, level: str) -> dict[str, str]:
    """Return appropriate sets/reps scheme based on goal and level."""
    goal = goal.lower()
    level = level.lower()

    if goal == "fat loss":
        if level == "beginner":
            return {"sets": "3", "reps": "12-15"}
        elif level == "intermediate":
            return {"sets": "4", "reps": "12-15"}
        else:
            return {"sets": "4", "reps": "15-20"}
    elif goal == "muscle gain":
        if level == "beginner":
            return {"sets": "3", "reps": "8-12"}
        elif level == "intermediate":
            return {"sets": "4", "reps": "8-12"}
        else:
            return {"sets": "5", "reps": "6-10"}
    else:  # maintenance
        if level == "beginner":
            return {"sets": "3", "reps": "10-12"}
        elif level == "intermediate":
            return {"sets": "3", "reps": "10-12"}
        else:
            return {"sets": "4", "reps": "8-12"}


# ---------------------------------------------------------------------------
# Diet planning engine (dataset-driven)
# ---------------------------------------------------------------------------

def _find_closest_nutrition_rows(
    daily_calories: int,
    dietary_preference: str,
    gender: str,
    n_candidates: int = 10,
) -> pd.DataFrame:
    """
    Find the closest matching rows from the nutrition dataset
    based on calorie target and dietary preference.
    """
    df, _ = load_nutrition_dataset()
    filtered = df.copy()

    # Filter by dietary preference if column exists
    if "Dietary Preference" in filtered.columns and dietary_preference.lower() != "any":
        pref_lower = dietary_preference.lower()
        pref_subset = filtered[
            filtered["Dietary Preference"].str.lower().str.contains(pref_lower, na=False)
        ]
        if len(pref_subset) >= 5:
            filtered = pref_subset

    # Filter by gender if column exists
    if "Gender" in filtered.columns and gender:
        gender_subset = filtered[
            filtered["Gender"].str.lower() == gender.lower()
        ]
        if len(gender_subset) >= 5:
            filtered = gender_subset

    # Sort by closest calorie match
    if "Daily Calorie Target" in filtered.columns:
        cal_col = "Daily Calorie Target"
    elif "Calories" in filtered.columns:
        cal_col = "Calories"
    else:
        # No calorie column; return random sample
        return filtered.sample(min(n_candidates, len(filtered)))

    filtered = filtered.copy()
    filtered["_cal_diff"] = (pd.to_numeric(filtered[cal_col], errors="coerce").fillna(2000) - daily_calories).abs()
    filtered = filtered.sort_values("_cal_diff").head(n_candidates)
    return filtered.drop(columns=["_cal_diff"], errors="ignore")


def _extract_meal_from_row(row: pd.Series, meal_type: str) -> dict[str, str]:
    """Extract a single meal suggestion and its macros from a nutrition row."""
    prefix_map = {
        "Breakfast Suggestion": ("Breakfast", "Breakfast"),
        "Lunch Suggestion": ("Lunch", "Lunch"),
        "Dinner Suggestion": ("Dinner", "Dinner"),
        "Snack Suggestion": ("Snack", "Snack"),
    }
    _, prefix = prefix_map.get(meal_type, ("", ""))

    name = str(row.get(meal_type, "")).strip()
    if not name or name == "nan":
        name = f"Healthy {prefix.lower()} option"

    # Try to get per-meal macros from the dataset
    cal = row.get(f"{prefix} Calories") or row.get(f"{prefix}s Calories")
    prot = row.get(f"{prefix} Protein") or row.get(f"{prefix}s Protein")
    carb = row.get(f"{prefix} Carbohydrates") or row.get(f"{prefix}s Carbohydrates")
    fat_val = row.get(f"{prefix} Fats") or row.get(f"{prefix}s Fats")

    # Convert to string with units, handling NaN
    def _fmt(val, unit="g"):
        try:
            v = float(val)
            if v != v:  # NaN check
                return "–"
            return f"{int(round(v))} {unit}"
        except (TypeError, ValueError):
            return "–"

    return {
        "name": name,
        "calories": _fmt(cal, "kcal"),
        "protein": _fmt(prot),
        "carbohydrates": _fmt(carb),
        "fat": _fmt(fat_val),
    }


def generate_diet_plan(
    daily_calories: int,
    goal: str,
    dietary_preference: str,
    gender: str = "",
) -> dict[str, Any]:
    """
    Generate a full-day diet plan using real data from the nutrition dataset.
    Falls back to macro-split based generation if dataset data is insufficient.
    """
    meal_slots = [
        "Breakfast Suggestion",
        "Lunch Suggestion",
        "Dinner Suggestion",
        "Snack Suggestion",
    ]

    plan: dict[str, Any] = {
        "daily_calorie_target": f"{daily_calories} kcal",
    }

    try:
        # Find closest matching rows from nutrition dataset
        candidates = _find_closest_nutrition_rows(
            daily_calories, dietary_preference, gender
        )

        if len(candidates) == 0:
            raise ValueError("No matching nutrition data found")

        # Pick meals from different rows for variety
        used_indices = set()

        for slot in meal_slots:
            # Find rows that have this meal suggestion
            available = candidates[
                candidates[slot].notna() & (candidates[slot].astype(str) != "nan")
            ] if slot in candidates.columns else pd.DataFrame()

            if len(available) > 0:
                # Pick a random row we haven't used for this slot type
                unused = available[~available.index.isin(used_indices)]
                if len(unused) > 0:
                    row = unused.sample(1).iloc[0]
                else:
                    row = available.sample(1).iloc[0]
                used_indices.add(row.name)

                meal = _extract_meal_from_row(row, slot)
                plan[slot] = [{
                    "name": meal["name"],
                    "calories": meal["calories"],
                    "protein": meal["protein"],
                    "carbohydrates": meal["carbohydrates"],
                    "fat": meal["fat"],
                }]
            else:
                # Fallback: generate based on macro split
                plan[slot] = [_generate_fallback_meal(slot, daily_calories, goal)]

    except Exception as exc:
        logger.warning("Diet plan from dataset failed (%s), using fallback.", exc)
        for slot in meal_slots:
            plan[slot] = [_generate_fallback_meal(slot, daily_calories, goal)]

    return plan


# ---------------------------------------------------------------------------
# Fallback meal generation (when dataset has insufficient data)
# ---------------------------------------------------------------------------

_FALLBACK_MEALS: dict[str, dict[str, list[str]]] = {
    "Breakfast Suggestion": {
        "omnivore": [
            "Scrambled eggs with whole-wheat toast and avocado",
            "Oatmeal with banana, walnuts, and whey protein",
            "Greek yoghurt with mixed berries and granola",
        ],
        "vegetarian": [
            "Oatmeal with banana, walnuts, and protein powder",
            "Greek yoghurt with mixed berries and granola",
            "Cottage cheese with pineapple and flaxseeds",
        ],
        "vegan": [
            "Smoothie: spinach, banana, oat milk, peanut butter",
            "Tofu scramble with vegetables and whole-grain toast",
            "Overnight oats with chia seeds, almond milk, and berries",
        ],
    },
    "Lunch Suggestion": {
        "omnivore": [
            "Grilled chicken breast with brown rice and steamed broccoli",
            "Tuna salad wrap with whole-wheat tortilla",
            "Salmon fillet with sweet potato and green beans",
        ],
        "vegetarian": [
            "Lentil and vegetable soup with a whole-grain roll",
            "Chickpea and quinoa salad with lemon-tahini dressing",
            "Paneer tikka with brown rice and raita",
        ],
        "vegan": [
            "Chickpea and quinoa salad with lemon-tahini dressing",
            "Black bean and veggie burrito bowl with brown rice",
            "Lentil and vegetable soup with whole-grain bread",
        ],
    },
    "Dinner Suggestion": {
        "omnivore": [
            "Baked cod with quinoa and roasted asparagus",
            "Lean beef stir-fry with mixed vegetables and jasmine rice",
            "Turkey meatballs with zucchini noodles and marinara sauce",
        ],
        "vegetarian": [
            "Tofu and vegetable curry with brown rice",
            "Eggplant parmesan with side salad",
            "Mushroom risotto with steamed vegetables",
        ],
        "vegan": [
            "Tofu and vegetable curry with brown rice",
            "Grilled tempeh with roasted sweet potato and steamed kale",
            "Stuffed bell peppers with quinoa and black beans",
        ],
    },
    "Snack Suggestion": {
        "omnivore": [
            "Apple with 2 tbsp almond butter",
            "Protein shake with oat milk",
            "Hard-boiled eggs (2) with cucumber",
        ],
        "vegetarian": [
            "Apple with 2 tbsp almond butter",
            "Rice cakes with cottage cheese and cucumber slices",
            "Mixed nuts and dried cranberries (30g)",
        ],
        "vegan": [
            "Edamame (150g) lightly salted",
            "Mixed nuts and dried cranberries (30g)",
            "Hummus with carrot and celery sticks",
        ],
    },
}

SLOT_FRACTIONS: dict[str, float] = {
    "Breakfast Suggestion": 0.25,
    "Lunch Suggestion": 0.35,
    "Dinner Suggestion": 0.30,
    "Snack Suggestion": 0.10,
}


def _generate_fallback_meal(
    slot: str,
    daily_calories: int,
    goal: str,
    dietary_preference: str = "omnivore",
) -> dict[str, str]:
    """Generate a meal entry when dataset data is unavailable."""
    pref = dietary_preference.lower()
    if pref not in _FALLBACK_MEALS.get(slot, {}):
        pref = "omnivore"

    names = _FALLBACK_MEALS.get(slot, {}).get(pref, ["Healthy meal"])
    name = random.choice(names)
    slot_cals = int(round(daily_calories * SLOT_FRACTIONS.get(slot, 0.25)))
    macros = split_macros(slot_cals, goal)

    return {
        "name": name,
        "calories": f"{slot_cals} kcal",
        "protein": f"{macros['protein']} g",
        "carbohydrates": f"{macros['carbohydrates']} g",
        "fat": f"{macros['fat']} g",
    }


# ---------------------------------------------------------------------------
# Master planner – orchestrates workout + diet
# ---------------------------------------------------------------------------

def generate_plan(
    age: int,
    gender: str,
    weight_kg: float,
    height_m: float,
    goal: str,
    workout_days: int,
    level: str,
    equipment: str,
    dietary_preference: str,
) -> dict[str, Any]:
    """Generate the full fitness + nutrition plan and return a JSON-ready dict."""

    # BMI
    bmi, bmi_category = calculate_bmi(weight_kg, height_m)

    # Calorie target
    daily_calories = calculate_daily_calories(
        age, gender, weight_kg, height_m, workout_days, goal
    )

    # Recommendations text
    recommendations = build_recommendations(bmi_category, goal, daily_calories, level)

    # Workout plan
    n_exercises = max(4, min(10, workout_days + 3))
    workout_plan = recommend_exercises(
        goal=goal,
        level=level,
        gender=gender,
        equipment=equipment,
        workout_days=workout_days,
        n_exercises=n_exercises,
    )

    # Diet plan (dataset-driven)
    diet_plan = generate_diet_plan(
        daily_calories=daily_calories,
        goal=goal,
        dietary_preference=dietary_preference,
        gender=gender,
    )

    return {
        "bmi": str(bmi),
        "bmi_category": bmi_category,
        "daily_calorie_target": f"{daily_calories} kcal",
        "recommendations": recommendations,
        "workout_plan": workout_plan,
        "diet_plan": diet_plan,
    }
