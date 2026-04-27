"""
data_loader.py – Dataset loader with automatic column detection.
Loads bundled CSV files from the datasets/ directory.
"""
from __future__ import annotations

import os
import logging
from functools import lru_cache
from difflib import SequenceMatcher
from typing import Optional

import pandas as pd

logger = logging.getLogger("fitlife.data_loader")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GYM_CSV = os.path.join(BASE_DIR, "datasets", "gym_exercise_dataset.csv")
NUTRITION_CSV = os.path.join(BASE_DIR, "datasets", "detailed_meals_macros_CLEANED.csv")

# ---------------------------------------------------------------------------
# Column alias schemas
# ---------------------------------------------------------------------------
WORKOUT_COLUMN_ALIASES: dict[str, list[str]] = {
    "Exercise Name": ["exercise name", "exercise", "name", "exercise_name", "name of exercise"],
    "Execution": ["execution", "description", "instructions", "how to", "steps", "technique"],
    "Main_muscle": ["main_muscle", "main muscle", "muscle group", "primary muscle", "body part", "muscle"],
    "Target_Muscles": ["target_muscles", "target muscles", "target muscle group", "muscles targeted", "target"],
    "Equipment": ["equipment", "equipment needed", "tool", "apparatus", "machine"],
    "Difficulty": ["difficulty (1-5)", "difficulty", "level", "intensity", "difficulty_level"],
    "Preparation": ["preparation", "setup", "starting position", "start"],
    "Mechanics": ["mechanics", "movement type", "type"],
    "Force": ["force", "force type", "direction"],
    "Secondary Muscles": ["secondary muscles", "secondary", "synergist_muscles", "synergist muscles"],
}

NUTRITION_COLUMN_ALIASES: dict[str, list[str]] = {
    "Ages": ["ages", "age", "user age", "patient age"],
    "Gender": ["gender", "sex", "user gender"],
    "Height": ["height", "height_cm", "user height"],
    "Weight": ["weight", "weight_kg", "user weight", "body weight"],
    "Activity Level": ["activity level", "activity", "physical activity", "exercise level"],
    "Dietary Preference": ["dietary preference", "diet type", "diet", "preference"],
    "Daily Calorie Target": ["daily calorie target", "calorie target", "target calories", "daily calories"],
    "Calories": ["calories", "total calories", "cal", "kcal", "caloric content"],
    "Protein": ["protein", "proteins", "protein (g)", "proteins (g)"],
    "Carbohydrates": ["carbohydrates", "carbs", "carbohydrates (g)", "carbs (g)"],
    "Fat": ["fat", "fats", "fat (g)", "fats (g)", "total fat"],
    "Fiber": ["fiber", "fibre", "dietary fiber"],
    "Breakfast Suggestion": ["breakfast suggestion", "breakfast", "breakfast meal"],
    "Breakfast Calories": ["breakfast calories", "breakfast cal"],
    "Breakfast Protein": ["breakfast protein"],
    "Breakfast Carbohydrates": ["breakfast carbohydrates", "breakfast carbs"],
    "Breakfast Fats": ["breakfast fats", "breakfast fat"],
    "Lunch Suggestion": ["lunch suggestion", "lunch", "lunch meal"],
    "Lunch Calories": ["lunch calories", "lunch cal"],
    "Lunch Protein": ["lunch protein"],
    "Lunch Carbohydrates": ["lunch carbohydrates", "lunch carbs"],
    "Lunch Fats": ["lunch fats", "lunch fat"],
    "Dinner Suggestion": ["dinner suggestion", "dinner", "dinner meal"],
    "Dinner Calories": ["dinner calories", "dinner cal"],
    "Dinner Protein": ["dinner protein", "dinner protein.1"],
    "Dinner Carbohydrates": ["dinner carbohydrates", "dinner carbohydrates.1", "dinner carbs"],
    "Dinner Fats": ["dinner fats", "dinner fat"],
    "Snack Suggestion": ["snack suggestion", "snack", "snack meal"],
    "Snack Calories": ["snacks calories", "snack calories", "snack cal"],
    "Snack Protein": ["snacks protein", "snack protein"],
    "Snack Carbohydrates": ["snacks carbohydrates", "snack carbohydrates", "snack carbs"],
    "Snack Fats": ["snacks fats", "snack fats", "snack fat"],
    "Disease": ["disease", "condition", "health condition", "disease label"],
}


# ---------------------------------------------------------------------------
# Fuzzy column matching
# ---------------------------------------------------------------------------
def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _best_match(actual_col: str, aliases: dict[str, list[str]], threshold: float = 0.55) -> Optional[str]:
    actual_lower = actual_col.lower().strip()
    best_target: Optional[str] = None
    best_score: float = 0.0
    for canonical, alias_list in aliases.items():
        if actual_lower == canonical.lower():
            return canonical
        for alias in alias_list:
            if actual_lower == alias:
                return canonical
        for alias in alias_list:
            score = _similarity(actual_lower, alias)
            if score > best_score and score >= threshold:
                best_score = score
                best_target = canonical
    return best_target


def auto_map_columns(df: pd.DataFrame, alias_schema: dict[str, list[str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    used_actuals: set[str] = set()
    for actual_col in df.columns:
        canonical = _best_match(actual_col, alias_schema, threshold=1.0)
        if canonical and canonical not in mapping:
            mapping[canonical] = actual_col
            used_actuals.add(actual_col)
    for actual_col in df.columns:
        if actual_col in used_actuals:
            continue
        canonical = _best_match(actual_col, alias_schema, threshold=0.55)
        if canonical and canonical not in mapping:
            mapping[canonical] = actual_col
            used_actuals.add(actual_col)
    return mapping


def rename_to_canonical(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    reverse = {actual: canonical for canonical, actual in mapping.items()}
    df = df.rename(columns=reverse)
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    return df


# ---------------------------------------------------------------------------
# Dataset loaders
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_workout_dataset() -> tuple[pd.DataFrame, dict[str, str]]:
    csv_path = os.environ.get("FITLIFE_GYM_CSV", GYM_CSV)
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Gym CSV not found at {csv_path}")
    raw = pd.read_csv(csv_path)
    raw.columns = raw.columns.str.strip()
    col_map = auto_map_columns(raw, WORKOUT_COLUMN_ALIASES)
    logger.info("Gym column mapping: %s", col_map)
    df = rename_to_canonical(raw, col_map)

    if "Exercise Name" not in df.columns:
        for col in df.columns:
            if "name" in col.lower() or "exercise" in col.lower():
                df = df.rename(columns={col: "Exercise Name"})
                break
        else:
            df["Exercise Name"] = "Exercise " + df.index.astype(str)
    if "Execution" not in df.columns:
        if "Preparation" in df.columns:
            df["Execution"] = df["Preparation"].fillna("Perform the exercise with controlled movement.")
        else:
            df["Execution"] = "Perform the exercise with controlled movement and proper form."
    if "Main_muscle" not in df.columns:
        if "Target_Muscles" in df.columns:
            df["Main_muscle"] = df["Target_Muscles"].str.split(",").str[0].str.strip()
        else:
            df["Main_muscle"] = "Full Body"
    if "Target_Muscles" not in df.columns:
        if "Main_muscle" in df.columns:
            df["Target_Muscles"] = df["Main_muscle"]
        else:
            df["Target_Muscles"] = "Full Body"
    for col in ["Target_Muscles", "Main_muscle", "Secondary Muscles"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.rstrip(",").str.strip()
    return df, col_map


@lru_cache(maxsize=1)
def load_nutrition_dataset() -> tuple[pd.DataFrame, dict[str, str]]:
    csv_path = os.environ.get("FITLIFE_NUTRITION_CSV", NUTRITION_CSV)
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Nutrition CSV not found at {csv_path}")
    raw = pd.read_csv(csv_path)
    raw.columns = raw.columns.str.strip()
    col_map = auto_map_columns(raw, NUTRITION_COLUMN_ALIASES)
    logger.info("Nutrition column mapping: %s", col_map)
    df = rename_to_canonical(raw, col_map)
    if "Calories" not in df.columns and "Daily Calorie Target" in df.columns:
        df["Calories"] = df["Daily Calorie Target"]
    for col in ["Protein", "Carbohydrates", "Fat"]:
        if col not in df.columns:
            df[col] = 0
    return df, col_map


def get_dataset_info() -> dict:
    info = {}
    try:
        gym_df, gym_map = load_workout_dataset()
        info["workout"] = {
            "rows": len(gym_df),
            "columns": list(gym_df.columns),
            "column_mapping": gym_map,
            "main_muscles": sorted(gym_df["Main_muscle"].dropna().unique().tolist()) if "Main_muscle" in gym_df.columns else [],
        }
    except Exception as exc:
        info["workout"] = {"error": str(exc)}
    try:
        nutr_df, nutr_map = load_nutrition_dataset()
        info["nutrition"] = {
            "rows": len(nutr_df),
            "columns": list(nutr_df.columns),
            "column_mapping": nutr_map,
            "dietary_preferences": sorted(nutr_df["Dietary Preference"].dropna().unique().tolist()) if "Dietary Preference" in nutr_df.columns else [],
        }
    except Exception as exc:
        info["nutrition"] = {"error": str(exc)}
    return info
