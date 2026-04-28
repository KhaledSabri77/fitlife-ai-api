from schemas import UserInput


# ──────────────────────────────────────────────
# BMI Calculation
# ──────────────────────────────────────────────

def calculate_bmi(weight: float, height: float) -> float:
    """BMI = weight (kg) / height (m)^2"""
    return round(weight / (height ** 2), 2)


def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


# ──────────────────────────────────────────────
# Calorie Target
# ──────────────────────────────────────────────

def calculate_daily_calories(user: UserInput, bmi_category: str) -> int:
    """Mifflin-St Jeor estimation + goal adjustment."""
    if user.gender.lower() in ("male", "m"):
        bmr = 10 * user.weight + 6.25 * (user.height * 100) - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * (user.height * 100) - 5 * user.age - 161

    # Activity multiplier based on workout days
    activity_map = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.725, 6: 1.725, 7: 1.9}
    tdee = bmr * activity_map.get(user.workout_days, 1.55)

    # Goal adjustment
    goal = user.goal.lower().replace(" ", "_")
    if goal in ("lose_weight", "fat_loss", "cut"):
        return int(tdee - 500)
    elif goal in ("gain_muscle", "bulk", "muscle_gain"):
        return int(tdee + 300)
    else:
        return int(tdee)


# ──────────────────────────────────────────────
# Recommendations
# ──────────────────────────────────────────────

def generate_recommendations(user: UserInput, bmi_category: str) -> str:
    goal = user.goal.lower().replace(" ", "_")
    parts = []

    if bmi_category == "Underweight":
        parts.append("Focus on calorie-surplus meals with adequate protein to build mass.")
    elif bmi_category in ("Overweight", "Obese"):
        parts.append("Prioritize a moderate calorie deficit with high-protein foods to preserve muscle.")
    else:
        parts.append("Maintain a balanced diet aligned with your fitness goal.")

    if goal in ("lose_weight", "fat_loss", "cut"):
        parts.append("Include 3-4 cardio sessions per week alongside resistance training.")
    elif goal in ("gain_muscle", "bulk", "muscle_gain"):
        parts.append("Emphasize progressive overload with compound lifts and sufficient rest days.")
    else:
        parts.append("Combine strength and cardiovascular training for overall fitness.")

    level = user.level.lower()
    if level == "beginner":
        parts.append("Start with lighter weights and master form before increasing intensity.")
    elif level == "advanced":
        parts.append("Incorporate advanced techniques like supersets, drop sets, and periodization.")

    return " ".join(parts)


# ──────────────────────────────────────────────
# Workout Plan
# ──────────────────────────────────────────────

_EXERCISE_POOL = {
    "chest": [
        {"Exercise Name": "Barbell Bench Press", "Execution": "Lie on a flat bench, lower the bar to your chest, press up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Anterior Deltoids", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Push-Ups", "Execution": "Start in plank position, lower body until chest nearly touches floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Dumbbell Flyes", "Execution": "Lie on bench with dumbbells, open arms wide then squeeze together", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "back": [
        {"Exercise Name": "Pull-Ups", "Execution": "Hang from bar with overhand grip, pull chin above bar", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps, Rhomboids", "Sets": "4", "Reps per Set": "6-10"},
        {"Exercise Name": "Barbell Rows", "Execution": "Bend over, pull barbell to lower chest, squeeze shoulder blades", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Biceps", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Seated Cable Row", "Execution": "Sit at cable machine, pull handle to torso, squeeze back", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Trapezius", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "legs": [
        {"Exercise Name": "Barbell Squat", "Execution": "Bar on upper back, squat until thighs are parallel, drive up", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Romanian Deadlift", "Execution": "Hold barbell, hinge at hips keeping legs slightly bent, lower bar along legs", "Main_muscle": "Legs", "Target_Muscles": "Hamstrings, Glutes, Lower Back", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Leg Press", "Execution": "Sit in leg press machine, push platform away, control the descent", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Walking Lunges", "Execution": "Step forward into lunge, alternate legs while walking", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "12 each leg"},
    ],
    "shoulders": [
        {"Exercise Name": "Overhead Press", "Execution": "Press barbell from shoulder level to overhead, lower slowly", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps, Upper Chest", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Lateral Raises", "Execution": "Hold dumbbells at sides, raise arms to shoulder height, lower slowly", "Main_muscle": "Shoulders", "Target_Muscles": "Lateral Deltoids", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "arms": [
        {"Exercise Name": "Barbell Curl", "Execution": "Stand with barbell, curl to shoulders keeping elbows stationary", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Brachialis", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Tricep Dips", "Execution": "Support body on parallel bars, lower and press up", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest, Anterior Deltoids", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "core": [
        {"Exercise Name": "Plank", "Execution": "Hold push-up position on forearms, keep body straight", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 seconds"},
        {"Exercise Name": "Hanging Leg Raises", "Execution": "Hang from bar, raise legs to 90 degrees, lower slowly", "Main_muscle": "Core", "Target_Muscles": "Lower Abs, Hip Flexors", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "cardio": [
        {"Exercise Name": "Treadmill Intervals", "Execution": "Alternate 1 min sprint with 2 min walk for 20 minutes", "Main_muscle": "Cardiovascular", "Target_Muscles": "Heart, Legs, Core", "Sets": "1", "Reps per Set": "20 min"},
        {"Exercise Name": "Jump Rope", "Execution": "Jump rope at moderate pace with brief rest intervals", "Main_muscle": "Cardiovascular", "Target_Muscles": "Calves, Shoulders, Core", "Sets": "3", "Reps per Set": "3 min"},
    ],
}

_BODYWEIGHT_POOL = {
    "chest": [
        {"Exercise Name": "Push-Ups", "Execution": "Start in plank position, lower body until chest nearly touches floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "4", "Reps per Set": "12-20"},
        {"Exercise Name": "Diamond Push-Ups", "Execution": "Hands close together under chest, lower and press up", "Main_muscle": "Chest", "Target_Muscles": "Inner Chest, Triceps", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "back": [
        {"Exercise Name": "Superman Hold", "Execution": "Lie face down, lift arms and legs off ground, hold", "Main_muscle": "Back", "Target_Muscles": "Erector Spinae, Glutes", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Inverted Rows (table)", "Execution": "Lie under sturdy table, pull chest to edge", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "legs": [
        {"Exercise Name": "Bodyweight Squats", "Execution": "Stand shoulder-width, squat until thighs parallel, stand up", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes", "Sets": "4", "Reps per Set": "15-20"},
        {"Exercise Name": "Glute Bridges", "Execution": "Lie on back, drive hips up squeezing glutes", "Main_muscle": "Legs", "Target_Muscles": "Glutes, Hamstrings", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Jump Squats", "Execution": "Squat down then explode upward, land softly", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Calves", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "shoulders": [
        {"Exercise Name": "Pike Push-Ups", "Execution": "In downward-dog position, bend elbows to lower head toward floor", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps", "Sets": "3", "Reps per Set": "8-12"},
    ],
    "arms": [
        {"Exercise Name": "Close-Grip Push-Ups", "Execution": "Push-up with hands close together targeting triceps", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Chin-Ups (door frame bar)", "Execution": "Underhand grip pull-up focusing on biceps", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Latissimus Dorsi", "Sets": "3", "Reps per Set": "6-10"},
    ],
    "core": _EXERCISE_POOL["core"],
    "cardio": [
        {"Exercise Name": "Burpees", "Execution": "Squat, kick back to plank, push-up, jump up", "Main_muscle": "Cardiovascular", "Target_Muscles": "Full Body", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "High Knees", "Execution": "Run in place bringing knees to chest height", "Main_muscle": "Cardiovascular", "Target_Muscles": "Core, Hip Flexors, Calves", "Sets": "3", "Reps per Set": "30 seconds"},
    ],
}


def _select_pool(equipment: str) -> dict:
    if equipment.lower() in ("none", "bodyweight", "no equipment"):
        return _BODYWEIGHT_POOL
    return _EXERCISE_POOL


def _muscle_split(workout_days: int) -> list[list[str]]:
    splits = {
        1: [["chest", "back", "legs", "core"]],
        2: [["chest", "back", "shoulders"], ["legs", "arms", "core"]],
        3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
        4: [["chest", "shoulders"], ["back"], ["legs"], ["arms", "core", "cardio"]],
        5: [["chest"], ["back"], ["legs"], ["shoulders", "arms"], ["core", "cardio"]],
        6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms", "core"], ["cardio"]],
        7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["cardio"]],
    }
    return splits.get(workout_days, splits[3])


def generate_workout_plan(user: UserInput) -> list[dict]:
    pool = _select_pool(user.equipment)
    split = _muscle_split(user.workout_days)

    exercises: list[dict] = []
    for day_muscles in split:
        for muscle in day_muscles:
            available = pool.get(muscle, [])
            pick = available[:2] if user.level.lower() != "beginner" else available[:1]
            exercises.extend(pick)

    if user.level.lower() == "beginner":
        for ex in exercises:
            ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))

    return exercises


# ──────────────────────────────────────────────
# Diet Plan
# ──────────────────────────────────────────────

_MEAL_DB = {
    "standard": {
        "Breakfast Suggestion": ["Scrambled eggs with whole-grain toast", "Greek yogurt with granola and berries", "Oatmeal with banana and peanut butter"],
        "Lunch Suggestion": ["Grilled chicken breast with brown rice and steamed broccoli", "Turkey and avocado wrap with side salad", "Salmon with quinoa and roasted vegetables"],
        "Dinner Suggestion": ["Lean steak with sweet potato and asparagus", "Baked chicken thighs with mixed vegetables", "Shrimp stir-fry with brown rice and bell peppers"],
        "Snack Suggestion": ["Mixed nuts and dried fruit", "Protein shake with banana", "Apple slices with almond butter"],
    },
    "vegetarian": {
        "Breakfast Suggestion": ["Veggie omelette with cheese and whole-grain toast", "Smoothie bowl with mixed berries and seeds", "Paneer paratha with yogurt"],
        "Lunch Suggestion": ["Chickpea curry with brown rice", "Caprese salad with quinoa", "Black bean and cheese quesadilla with guacamole"],
        "Dinner Suggestion": ["Stuffed bell peppers with rice and beans", "Vegetable stir-fry with tofu and noodles", "Eggplant parmesan with side salad"],
        "Snack Suggestion": ["Trail mix with dark chocolate chips", "Cottage cheese with pineapple", "Hummus with carrot and celery sticks"],
    },
    "vegan": {
        "Breakfast Suggestion": ["Chia seed pudding with coconut milk and mango", "Avocado toast on sourdough with cherry tomatoes", "Smoothie with spinach, banana, and plant protein"],
        "Lunch Suggestion": ["Lentil soup with crusty bread", "Buddha bowl with roasted chickpeas, sweet potato, and tahini", "Vegan burrito with black beans, rice, and salsa"],
        "Dinner Suggestion": ["Tofu stir-fry with vegetables and brown rice", "Spaghetti with marinara and roasted vegetables", "Stuffed sweet potatoes with black beans and avocado"],
        "Snack Suggestion": ["Edamame with sea salt", "Energy balls with oats, dates, and coconut", "Rice cakes with almond butter"],
    },
    "keto": {
        "Breakfast Suggestion": ["Bacon and eggs with avocado", "Keto smoothie with MCT oil, spinach, and almond milk", "Cream cheese pancakes with sugar-free syrup"],
        "Lunch Suggestion": ["Grilled chicken Caesar salad (no croutons)", "Bunless cheeseburger with lettuce wrap", "Tuna salad stuffed avocado"],
        "Dinner Suggestion": ["Salmon with butter-sautéed asparagus", "Pork chops with creamed spinach", "Chicken thighs with roasted cauliflower mash"],
        "Snack Suggestion": ["Cheese crisps", "Pork rinds with guacamole", "Handful of macadamia nuts"],
    },
}


def generate_diet_plan(user: UserInput, daily_calories: int) -> dict:
    pref = user.dietary_preference.lower().strip()
    meals = _MEAL_DB.get(pref, _MEAL_DB["standard"])

    return {
        "daily_calorie_target": str(daily_calories),
        "Breakfast Suggestion": meals["Breakfast Suggestion"],
        "Lunch Suggestion": meals["Lunch Suggestion"],
        "Dinner Suggestion": meals["Dinner Suggestion"],
        "Snack Suggestion": meals["Snack Suggestion"],
    }


# ──────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────

def generate_plan(user: UserInput) -> dict:
    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)
    daily_calories = calculate_daily_calories(user, bmi_category)
    recommendations = generate_recommendations(user, bmi_category)
    workout_plan = generate_workout_plan(user)
    diet_plan = generate_diet_plan(user, daily_calories)

    return {
        "bmi": str(bmi),
        "bmi_category": bmi_category,
        "daily_calorie_target": str(daily_calories),
        "recommendations": recommendations,
        "workout_plan": workout_plan,
        "diet_plan": diet_plan,
    }
