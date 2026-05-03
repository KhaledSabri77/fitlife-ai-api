from schemas import UserInput

# ── Workout Plan ──

_EX = {
    "chest": [
        {"Exercise Name": "Barbell Bench Press", "Execution": "Lie on flat bench, lower bar to chest, press up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Anterior Deltoids", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Push-Ups", "Execution": "Plank position, lower chest to floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Dumbbell Flyes", "Execution": "Lie on bench, open arms wide with dumbbells, squeeze together", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
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
        {"Exercise Name": "Treadmill Intervals", "Execution": "Alternate 1 min sprint with 2 min walk for 20 min", "Main_muscle": "Cardiovascular", "Target_Muscles": "Heart, Legs, Core", "Sets": "1", "Reps per Set": "20 min"},
        {"Exercise Name": "Jump Rope", "Execution": "Jump rope at moderate pace with brief rest intervals", "Main_muscle": "Cardiovascular", "Target_Muscles": "Calves, Shoulders, Core", "Sets": "3", "Reps per Set": "3 min"},
    ],
}

_BW = {
    "chest": [
        {"Exercise Name": "Push-Ups", "Execution": "Plank position, lower chest to floor, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "4", "Reps per Set": "12-20"},
        {"Exercise Name": "Diamond Push-Ups", "Execution": "Hands close together under chest, lower and press up", "Main_muscle": "Chest", "Target_Muscles": "Inner Chest, Triceps", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "back": [
        {"Exercise Name": "Superman Hold", "Execution": "Lie face down, lift arms and legs off ground, hold", "Main_muscle": "Back", "Target_Muscles": "Erector Spinae, Glutes", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Inverted Rows", "Execution": "Lie under sturdy table, pull chest to edge", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps", "Sets": "3", "Reps per Set": "10-12"},
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
    "core": _EX["core"],
    "cardio": [
        {"Exercise Name": "Burpees", "Execution": "Squat, kick back to plank, push-up, jump up", "Main_muscle": "Cardiovascular", "Target_Muscles": "Full Body", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "High Knees", "Execution": "Run in place bringing knees to chest height", "Main_muscle": "Cardiovascular", "Target_Muscles": "Core, Hip Flexors, Calves", "Sets": "3", "Reps per Set": "30 seconds"},
    ],
}

def _select_pool(workoutLocation: str) -> dict:
    if workoutLocation.lower() in ("home", "outdoor", "none", "bodyweight", "no equipment"):
        return _BW
    return _EX

def _muscle_split(days: int) -> list[list[str]]:
    s = {
        1: [["chest", "back", "legs", "core"]],
        2: [["chest", "back", "shoulders"], ["legs", "arms", "core"]],
        3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
        4: [["chest", "shoulders"], ["back"], ["legs"], ["arms", "core", "cardio"]],
        5: [["chest"], ["back"], ["legs"], ["shoulders", "arms"], ["core", "cardio"]],
        6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms", "core"], ["cardio"]],
        7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["cardio"]],
    }
    return s.get(days, s[3])

def generate_workout_plan(user: UserInput) -> list[dict]:
    pool = _select_pool(user.workoutLocation)
    split = _muscle_split(user.workoutDays)
    exercises: list[dict] = []
    for day_muscles in split:
        for muscle in day_muscles:
            available = pool.get(muscle, [])
            pick = available[:2] if user.experienceLevel.lower() != "beginner" else available[:1]
            exercises.extend(pick)
    # Guarantee at least 4 exercises
    if len(exercises) < 4:
        for ex in pool.get("legs", []) + pool.get("core", []):
            if ex not in exercises:
                exercises.append(ex)
            if len(exercises) >= 4:
                break
    if user.experienceLevel.lower() == "beginner":
        for ex in exercises:
            ex["Sets"] = str(max(2, int(ex["Sets"]) - 1))
    return exercises

# ── Orchestrator ──

def generate_plan(user: UserInput) -> dict:
    workout_plan = generate_workout_plan(user)
    return {
        "workout_plan": workout_plan,
    }
