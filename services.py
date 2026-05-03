"""
services.py - FitLife AI business logic layer.

All functions are stateless and safe for concurrent use.
Exercise databases are NEVER mutated — deep copies are used
whenever modifications (e.g. beginner set adjustments) are needed.

Architecture (logical sections):
    1. bmi_service      — BMI calculation & classification
    2. nutrition_service — Mifflin-St Jeor calorie estimation
    3. recommendation_service — structured advice generation
    4. workout_service   — equipment-aware, day-grouped workout builder
    5. orchestrator      — composes all services into a single response
"""

import copy
from enum import Enum
from typing import Dict, List

from schemas import (
    ExperienceLevel,
    FitnessGoal,
    Gender,
    UserInput,
    WorkoutLocation,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. BMI Service
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class BMICategory(str, Enum):
    """WHO BMI classification thresholds."""
    UNDERWEIGHT = "Underweight"
    NORMAL = "Normal weight"
    OVERWEIGHT = "Overweight"
    OBESE = "Obese"


# Ordered thresholds — evaluated top-to-bottom, first match wins
_BMI_THRESHOLDS: list[tuple[float, BMICategory]] = [
    (18.5, BMICategory.UNDERWEIGHT),
    (25.0, BMICategory.NORMAL),
    (30.0, BMICategory.OVERWEIGHT),
]


def calculate_bmi(weight: float, height: float) -> float:
    """Calculate Body Mass Index.

    Args:
        weight: Body weight in kilograms.
        height: Height in meters.

    Returns:
        BMI rounded to two decimal places.

    Raises:
        ValueError: If height is zero or negative.
    """
    if height <= 0:
        raise ValueError("Height must be a positive number.")
    return round(weight / (height ** 2), 2)


def get_bmi_category(bmi: float) -> BMICategory:
    """Classify a BMI value into a WHO category.

    Uses ordered threshold list instead of fragile if/elif chains.

    Args:
        bmi: Calculated BMI value.

    Returns:
        BMICategory enum member.
    """
    for threshold, category in _BMI_THRESHOLDS:
        if bmi < threshold:
            return category
    return BMICategory.OBESE


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Nutrition Service
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# Single source of truth — used by both services.py and main.py
ACTIVITY_MULTIPLIERS: Dict[str, float] = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Goal-specific calorie offsets
_GOAL_CALORIE_OFFSET: Dict[FitnessGoal, int] = {
    FitnessGoal.LOSE_WEIGHT: -500,
    FitnessGoal.GAIN_MUSCLE: 300,
    FitnessGoal.MAINTAIN: 0,
}


def calculate_daily_calories(user: UserInput) -> int:
    """Estimate daily calorie target using Mifflin-St Jeor equation.

    Applies activity multiplier from user's stated activity level
    and adjusts for fitness goal.

    Args:
        user: Validated user input.

    Returns:
        Integer calorie target (minimum 1200 kcal safety floor).
    """
    height_cm = user.height * 100

    if user.gender == Gender.MALE:
        bmr = 10 * user.weight + 6.25 * height_cm - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * height_cm - 5 * user.age - 161

    multiplier = ACTIVITY_MULTIPLIERS.get(
        user.activityLevel.lower(), 1.55
    )
    tdee = bmr * multiplier

    offset = _GOAL_CALORIE_OFFSET.get(user.fitnessGoal, 0)
    target = int(tdee + offset)

    # Safety floor — never recommend below 1200 kcal
    return max(1200, target)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Recommendation Service
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def generate_recommendations(
    user: UserInput,
    bmi_category: BMICategory,
) -> List[Dict[str, str]]:
    """Build structured recommendation list.

    Returns a list of {category, message} dicts instead of a flat
    string, making it easy for mobile clients to render sections.

    Args:
        user: Validated user input.
        bmi_category: Pre-computed BMI classification.

    Returns:
        List of recommendation dicts with 'category' and 'message'.
    """
    recs: List[Dict[str, str]] = []

    # — BMI-based advice —
    bmi_advice = {
        BMICategory.UNDERWEIGHT: (
            "Focus on calorie-surplus meals with adequate protein "
            "to build mass safely."
        ),
        BMICategory.OVERWEIGHT: (
            "Prioritize a moderate calorie deficit with high-protein "
            "foods to preserve muscle."
        ),
        BMICategory.OBESE: (
            "Consult a healthcare professional. Focus on sustainable "
            "calorie deficit and low-impact cardio."
        ),
        BMICategory.NORMAL: (
            "Maintain a balanced diet aligned with your fitness goal."
        ),
    }
    recs.append({
        "category": "nutrition",
        "message": bmi_advice.get(
            bmi_category,
            "Maintain a balanced diet aligned with your fitness goal."
        ),
    })

    # — Goal-based advice —
    goal_advice = {
        FitnessGoal.LOSE_WEIGHT: (
            "Include 3-4 cardio sessions per week alongside "
            "resistance training for optimal fat loss."
        ),
        FitnessGoal.GAIN_MUSCLE: (
            "Emphasize progressive overload with compound lifts "
            "and ensure sufficient rest days."
        ),
        FitnessGoal.MAINTAIN: (
            "Combine strength and cardiovascular training "
            "for overall fitness maintenance."
        ),
    }
    recs.append({
        "category": "training",
        "message": goal_advice.get(
            user.fitnessGoal,
            "Follow a balanced training program."
        ),
    })

    # — Experience-based advice —
    level_advice = {
        ExperienceLevel.BEGINNER: (
            "Start with lighter weights and master form "
            "before increasing intensity."
        ),
        ExperienceLevel.ADVANCED: (
            "Incorporate advanced techniques like supersets, "
            "drop sets, and periodization."
        ),
    }
    if user.experienceLevel in level_advice:
        recs.append({
            "category": "experience",
            "message": level_advice[user.experienceLevel],
        })

    # — Recovery advice —
    if user.workoutDays <= 2:
        recs.append({
            "category": "recovery",
            "message": (
                "Consider adding an extra day for active recovery "
                "like walking or yoga."
            ),
        })
    elif user.workoutDays >= 6:
        recs.append({
            "category": "recovery",
            "message": (
                "Ensure at least one full rest day per week "
                "for proper recovery."
            ),
        })

    return recs


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Workout Service — Exercise Database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Gym / full-equipment pool
_GYM_EXERCISES: Dict[str, List[Dict]] = {
    "chest": [
        {"Exercise Name": "Barbell Bench Press", "Execution": "Lie on flat bench, lower bar to chest, press up explosively", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Anterior Deltoids", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Dumbbell Flyes", "Execution": "Lie on bench, open arms wide with dumbbells, squeeze together", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Incline Dumbbell Press", "Execution": "On incline bench, press dumbbells up from chest level", "Main_muscle": "Chest", "Target_Muscles": "Upper Pectorals, Triceps, Anterior Deltoids", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "back": [
        {"Exercise Name": "Pull-Ups", "Execution": "Overhand grip on bar, pull chin above bar", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps, Rhomboids", "Sets": "4", "Reps per Set": "6-10"},
        {"Exercise Name": "Barbell Rows", "Execution": "Bend over, pull barbell to lower chest, squeeze shoulder blades", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Biceps", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Seated Cable Row", "Execution": "Sit at cable machine, pull handle to torso, squeeze back", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Trapezius", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "legs": [
        {"Exercise Name": "Barbell Squat", "Execution": "Bar on upper back, squat to parallel, drive up", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Romanian Deadlift", "Execution": "Hinge at hips with barbell, lower along legs, squeeze glutes up", "Main_muscle": "Legs", "Target_Muscles": "Hamstrings, Glutes, Lower Back", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Leg Press", "Execution": "Sit in leg press machine, push platform away, control descent", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Walking Lunges", "Execution": "Step forward into lunge, alternate legs while walking", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "12 each leg"},
    ],
    "shoulders": [
        {"Exercise Name": "Overhead Press", "Execution": "Press barbell from shoulders to overhead, lower slowly", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps, Upper Chest", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Lateral Raises", "Execution": "Raise dumbbells to shoulder height out to sides, lower slowly", "Main_muscle": "Shoulders", "Target_Muscles": "Lateral Deltoids", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "arms": [
        {"Exercise Name": "Barbell Curl", "Execution": "Curl barbell to shoulders keeping elbows stationary", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Brachialis", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Tricep Dips", "Execution": "Support body on parallel bars, lower and press up", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest, Anterior Deltoids", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "core": [
        {"Exercise Name": "Plank", "Execution": "Hold forearm plank keeping body straight", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 seconds"},
        {"Exercise Name": "Hanging Leg Raises", "Execution": "Hang from bar, raise legs to 90 degrees, lower slowly", "Main_muscle": "Core", "Target_Muscles": "Lower Abs, Hip Flexors", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "cardio": [
        {"Exercise Name": "Treadmill Intervals", "Execution": "Alternate 1 min sprint with 2 min walk for 20 minutes", "Main_muscle": "Cardiovascular", "Target_Muscles": "Heart, Legs, Core", "Sets": "1", "Reps per Set": "20 min"},
        {"Exercise Name": "Jump Rope", "Execution": "Jump rope at moderate pace with brief rest intervals", "Main_muscle": "Cardiovascular", "Target_Muscles": "Calves, Shoulders, Core", "Sets": "3", "Reps per Set": "3 min"},
    ],
}

# Bodyweight / home / outdoor pool (independent copy of core)
_BODYWEIGHT_EXERCISES: Dict[str, List[Dict]] = {
    "chest": [
        {"Exercise Name": "Push-Ups", "Execution": "Plank position, lower chest to floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "4", "Reps per Set": "12-20"},
        {"Exercise Name": "Diamond Push-Ups", "Execution": "Hands close together under chest, lower and press up", "Main_muscle": "Chest", "Target_Muscles": "Inner Chest, Triceps", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "back": [
        {"Exercise Name": "Superman Hold", "Execution": "Lie face down, lift arms and legs off ground, hold", "Main_muscle": "Back", "Target_Muscles": "Erector Spinae, Glutes", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Inverted Rows", "Execution": "Lie under sturdy surface, pull chest up to edge", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "legs": [
        {"Exercise Name": "Bodyweight Squats", "Execution": "Stand shoulder-width, squat to parallel, stand up", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes", "Sets": "4", "Reps per Set": "15-20"},
        {"Exercise Name": "Glute Bridges", "Execution": "Lie on back, drive hips up squeezing glutes", "Main_muscle": "Legs", "Target_Muscles": "Glutes, Hamstrings", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Jump Squats", "Execution": "Squat down then explode upward, land softly", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Calves", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "shoulders": [
        {"Exercise Name": "Pike Push-Ups", "Execution": "Downward-dog position, bend elbows to lower head toward floor", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "arms": [
        {"Exercise Name": "Close-Grip Push-Ups", "Execution": "Push-up with hands close together targeting triceps", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Chin-Ups", "Execution": "Underhand grip pull-up focusing on biceps", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Latissimus Dorsi", "Sets": "3", "Reps per Set": "6-10"},
    ],
    "core": [
        {"Exercise Name": "Plank", "Execution": "Hold forearm plank keeping body straight", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 seconds"},
        {"Exercise Name": "Mountain Climbers", "Execution": "Plank position, alternate driving knees to chest rapidly", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Hip Flexors, Shoulders", "Sets": "3", "Reps per Set": "20 each side"},
    ],
    "cardio": [
        {"Exercise Name": "Burpees", "Execution": "Squat, kick back to plank, push-up, jump up", "Main_muscle": "Cardiovascular", "Target_Muscles": "Full Body", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "High Knees", "Execution": "Run in place bringing knees to chest height", "Main_muscle": "Cardiovascular", "Target_Muscles": "Core, Hip Flexors, Calves", "Sets": "3", "Reps per Set": "30 seconds"},
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4b. Workout Service — Plan Builder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _select_exercise_pool(location: WorkoutLocation) -> Dict[str, List[Dict]]:
    """Return the exercise database matching the user's training location.

    Args:
        location: Where the user trains.

    Returns:
        Immutable reference to the appropriate exercise pool.
    """
    if location in (WorkoutLocation.HOME, WorkoutLocation.OUTDOOR):
        return _BODYWEIGHT_EXERCISES
    return _GYM_EXERCISES


# Day-to-muscle-group mapping by number of training days
_MUSCLE_SPLITS: Dict[int, List[List[str]]] = {
    1: [["chest", "back", "legs", "core"]],
    2: [["chest", "back", "shoulders"], ["legs", "arms", "core"]],
    3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
    4: [["chest", "shoulders"], ["back"], ["legs"], ["arms", "core", "cardio"]],
    5: [["chest"], ["back"], ["legs"], ["shoulders", "arms"], ["core", "cardio"]],
    6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms", "core"], ["cardio"]],
    7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["cardio"]],
}

_DEFAULT_SPLIT_DAYS = 3
_MIN_EXERCISES_PER_DAY = 2


def generate_workout_plan(user: UserInput) -> List[Dict]:
    """Build a day-grouped workout plan.

    Returns a list of day objects:
        [
            {
                "day": "Day 1",
                "muscles": ["chest", "shoulders"],
                "exercises": [ {exercise dict}, ... ]
            },
            ...
        ]

    Key safety measures:
        - Deep-copies exercises so the global pool is never mutated.
        - Handles missing muscle groups gracefully.
        - Guarantees minimum exercises per day via fallback.

    Args:
        user: Validated user input.

    Returns:
        List of day dicts, each containing muscles and exercises.
    """
    pool = _select_exercise_pool(user.workoutLocation)
    split = _MUSCLE_SPLITS.get(user.workoutDays, _MUSCLE_SPLITS[_DEFAULT_SPLIT_DAYS])

    is_beginner = user.experienceLevel == ExperienceLevel.BEGINNER
    pick_count = 1 if is_beginner else 2

    workout_days: List[Dict] = []

    for day_index, day_muscles in enumerate(split, start=1):
        day_exercises: List[Dict] = []

        for muscle in day_muscles:
            available = pool.get(muscle, [])
            if not available:
                continue
            # Deep copy to prevent global mutation
            selected = copy.deepcopy(available[:pick_count])
            day_exercises.extend(selected)

        # Fallback — guarantee minimum exercises per day
        if len(day_exercises) < _MIN_EXERCISES_PER_DAY:
            for fallback_group in ("legs", "core"):
                for ex in pool.get(fallback_group, []):
                    candidate = copy.deepcopy(ex)
                    if candidate not in day_exercises:
                        day_exercises.append(candidate)
                    if len(day_exercises) >= _MIN_EXERCISES_PER_DAY:
                        break
                if len(day_exercises) >= _MIN_EXERCISES_PER_DAY:
                    break

        # Beginner adjustment — reduce sets (on the COPY, not original)
        if is_beginner:
            for ex in day_exercises:
                try:
                    ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))
                except (ValueError, KeyError):
                    pass

        workout_days.append({
            "day": f"Day {day_index}",
            "muscles": day_muscles,
            "exercises": day_exercises,
        })

    return workout_days


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Orchestrator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def generate_plan(user: UserInput) -> dict:
    """Compose all services into the final plan response.

    Stateless — safe for concurrent FastAPI requests.

    Args:
        user: Validated user input from the request body.

    Returns:
        Dict matching the PlanResponse schema.
    """
    # BMI
    bmi_value = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi_value)

    # Nutrition
    daily_calories = calculate_daily_calories(user)

    # Recommendations
    recommendations = generate_recommendations(user, bmi_category)

    # Workout
    workout_plan = generate_workout_plan(user)

    return {
        "bmi": {
            "value": bmi_value,
            "category": bmi_category.value,
        },
        "nutrition": {
            "daily_calorie_target": daily_calories,
        },
        "recommendations": recommendations,
        "workout_plan": workout_plan,
    }
