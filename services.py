from schemas import UserInput


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BMI Calculation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bmi(weight: float, height: float) -> float:
    if weight <= 0 or height <= 0:
        raise ValueError("Height and weight must be positive values")

    bmi = weight / (height ** 2)

    return round(bmi, 2)


def get_bmi_category(bmi: float) -> str:
    if bmi <= 0:
        return "Invalid BMI"

    elif bmi < 18.5:
        return "Underweight"

    elif 18.5 <= bmi < 25:
        return "Normal Weight"

    elif 25 <= bmi < 30:
        return "Overweight"

    elif 30 <= bmi < 35:
        return "Obesity Class I"

    elif 35 <= bmi < 40:
        return "Obesity Class II"

    else:
        return "Obesity Class III"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Exercise Database — Gym
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GYM_EXERCISES = {
    "chest": [
        {"Exercise Name": "Barbell Bench Press", "Execution": "Lie on flat bench, grip bar shoulder-width, lower to mid-chest, press up explosively", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Anterior Deltoids", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Incline Dumbbell Press", "Execution": "Set bench to 30-45 degrees, press dumbbells from chest to full lockout", "Main_muscle": "Chest", "Target_Muscles": "Upper Pectorals, Triceps, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Dumbbell Flyes", "Execution": "Lie flat, lower dumbbells in wide arc until stretch in chest, squeeze back together", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Cable Crossovers", "Execution": "Stand between cable towers, pull handles downward and together in arc motion", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Anterior Deltoids", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "back": [
        {"Exercise Name": "Barbell Bent-Over Row", "Execution": "Bend at 45 degrees, pull barbell to lower chest, squeeze shoulder blades together", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Biceps", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Pull-Ups", "Execution": "Overhand grip on bar, pull chin above bar, lower with full control", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps, Rhomboids", "Sets": "4", "Reps per Set": "6-10"},
        {"Exercise Name": "Seated Cable Row", "Execution": "Sit upright at cable station, pull handle to torso, retract shoulder blades", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Rhomboids, Trapezius", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Lat Pulldown", "Execution": "Grip wide bar overhead, pull to upper chest, control the eccentric", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Teres Major, Biceps", "Sets": "3", "Reps per Set": "10-12"},
    ],
    "legs": [
        {"Exercise Name": "Barbell Back Squat", "Execution": "Bar on upper traps, squat to parallel or below, drive up through heels", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Romanian Deadlift", "Execution": "Hinge at hips keeping bar close to legs, feel hamstring stretch, squeeze glutes to return", "Main_muscle": "Legs", "Target_Muscles": "Hamstrings, Glutes, Lower Back", "Sets": "4", "Reps per Set": "8-12"},
        {"Exercise Name": "Leg Press", "Execution": "Sit in machine with feet shoulder-width, push platform away, control descent", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Walking Lunges", "Execution": "Step forward into deep lunge, drive through front heel, alternate legs", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "12 each leg"},
    ],
    "shoulders": [
        {"Exercise Name": "Overhead Barbell Press", "Execution": "Press barbell from front shoulders to full lockout overhead, lower with control", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps, Upper Chest", "Sets": "4", "Reps per Set": "8-10"},
        {"Exercise Name": "Dumbbell Lateral Raises", "Execution": "Raise dumbbells out to sides until shoulder height, lower slowly", "Main_muscle": "Shoulders", "Target_Muscles": "Lateral Deltoids", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Face Pulls", "Execution": "Pull rope attachment to face height, externally rotate hands at peak contraction", "Main_muscle": "Shoulders", "Target_Muscles": "Rear Deltoids, Rotator Cuff, Trapezius", "Sets": "3", "Reps per Set": "15-20"},
    ],
    "arms": [
        {"Exercise Name": "Barbell Curl", "Execution": "Curl barbell to shoulders keeping elbows pinned at sides, lower under control", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Brachialis", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Tricep Dips", "Execution": "Support body on parallel bars, lower until upper arms are parallel, press up", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest, Anterior Deltoids", "Sets": "3", "Reps per Set": "8-12"},
        {"Exercise Name": "Dumbbell Hammer Curls", "Execution": "Curl dumbbells with neutral palms-facing grip, squeeze at top", "Main_muscle": "Arms", "Target_Muscles": "Brachialis, Biceps, Forearms", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Cable Tricep Pushdowns", "Execution": "Push cable bar straight down, fully extend arms, squeeze triceps at bottom", "Main_muscle": "Arms", "Target_Muscles": "Triceps", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "core": [
        {"Exercise Name": "Plank Hold", "Execution": "Hold forearm plank with body in straight line, brace core throughout", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 seconds"},
        {"Exercise Name": "Hanging Leg Raises", "Execution": "Hang from bar, raise legs to 90 degrees, lower slowly without swinging", "Main_muscle": "Core", "Target_Muscles": "Lower Abs, Hip Flexors", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "Cable Woodchops", "Execution": "Rotate torso diagonally pulling cable from high to low across body", "Main_muscle": "Core", "Target_Muscles": "Obliques, Rectus Abdominis, Serratus", "Sets": "3", "Reps per Set": "12 each side"},
    ],
    "cardio": [
        {"Exercise Name": "Treadmill HIIT Intervals", "Execution": "Alternate 1 min sprint at 80-90% effort with 2 min recovery walk", "Main_muscle": "Cardiovascular", "Target_Muscles": "Heart, Quadriceps, Calves, Core", "Sets": "1", "Reps per Set": "20 minutes"},
        {"Exercise Name": "Rowing Machine Intervals", "Execution": "Row at high intensity with full leg drive for 500m, rest 1 min, repeat", "Main_muscle": "Cardiovascular", "Target_Muscles": "Back, Legs, Arms, Core", "Sets": "1", "Reps per Set": "15 minutes"},
    ],
    "mobility": [
        {"Exercise Name": "Hip Flexor Stretch", "Execution": "Kneel in lunge position, push hips forward, hold stretch for 30 seconds each side", "Main_muscle": "Mobility", "Target_Muscles": "Hip Flexors, Quadriceps", "Sets": "2", "Reps per Set": "30 seconds each side"},
        {"Exercise Name": "Cat-Cow Stretch", "Execution": "On hands and knees, alternate arching and rounding the spine rhythmically", "Main_muscle": "Mobility", "Target_Muscles": "Spine, Core, Shoulders", "Sets": "2", "Reps per Set": "10 reps"},
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Exercise Database — Home / Bodyweight
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOME_EXERCISES = {
    "chest": [
        {"Exercise Name": "Standard Push-Ups", "Execution": "Plank position, lower chest to floor with elbows at 45 degrees, push back up", "Main_muscle": "Chest", "Target_Muscles": "Pectorals, Triceps, Core", "Sets": "4", "Reps per Set": "12-20"},
        {"Exercise Name": "Diamond Push-Ups", "Execution": "Hands together forming diamond shape under chest, lower and press up", "Main_muscle": "Chest", "Target_Muscles": "Inner Chest, Triceps", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "Decline Push-Ups", "Execution": "Feet elevated on chair or step, perform push-up targeting upper chest", "Main_muscle": "Chest", "Target_Muscles": "Upper Pectorals, Triceps, Anterior Deltoids", "Sets": "3", "Reps per Set": "10-15"},
    ],
    "back": [
        {"Exercise Name": "Superman Hold", "Execution": "Lie face down, simultaneously lift arms and legs off ground, squeeze and hold", "Main_muscle": "Back", "Target_Muscles": "Erector Spinae, Glutes, Rear Deltoids", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Inverted Rows", "Execution": "Lie under sturdy table edge, grip edge, pull chest up to table", "Main_muscle": "Back", "Target_Muscles": "Latissimus Dorsi, Biceps, Rhomboids", "Sets": "3", "Reps per Set": "10-12"},
        {"Exercise Name": "Reverse Snow Angels", "Execution": "Lie face down, sweep arms from hips to overhead while squeezing back muscles", "Main_muscle": "Back", "Target_Muscles": "Rhomboids, Rear Deltoids, Trapezius", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "legs": [
        {"Exercise Name": "Bodyweight Squats", "Execution": "Feet shoulder-width, sit hips back to parallel, drive up through heels", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "4", "Reps per Set": "15-20"},
        {"Exercise Name": "Glute Bridges", "Execution": "Lie on back with knees bent, drive hips up squeezing glutes at top, lower slowly", "Main_muscle": "Legs", "Target_Muscles": "Glutes, Hamstrings", "Sets": "3", "Reps per Set": "15-20"},
        {"Exercise Name": "Jump Squats", "Execution": "Squat down then explode upward into jump, land softly with bent knees", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Calves", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Bulgarian Split Squats", "Execution": "Rear foot elevated on chair, lower into single-leg squat, drive up through front heel", "Main_muscle": "Legs", "Target_Muscles": "Quadriceps, Glutes, Hamstrings", "Sets": "3", "Reps per Set": "10 each leg"},
    ],
    "shoulders": [
        {"Exercise Name": "Pike Push-Ups", "Execution": "Hips high in inverted V position, bend elbows to lower head toward floor, press up", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Triceps, Upper Chest", "Sets": "3", "Reps per Set": "8-12"},
        {"Exercise Name": "Wall Handstand Hold", "Execution": "Kick up into handstand against wall, hold with arms locked and core braced", "Main_muscle": "Shoulders", "Target_Muscles": "Deltoids, Trapezius, Core", "Sets": "3", "Reps per Set": "15-30 seconds"},
    ],
    "arms": [
        {"Exercise Name": "Close-Grip Push-Ups", "Execution": "Push-up with hands directly under shoulders, elbows tight to body", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Chest, Anterior Deltoids", "Sets": "3", "Reps per Set": "12-15"},
        {"Exercise Name": "Chin-Ups", "Execution": "Underhand grip on bar or ledge, pull chin above hands, lower with control", "Main_muscle": "Arms", "Target_Muscles": "Biceps, Latissimus Dorsi", "Sets": "3", "Reps per Set": "6-10"},
        {"Exercise Name": "Tricep Bench Dips", "Execution": "Hands on chair edge behind you, lower body by bending elbows to 90 degrees, press up", "Main_muscle": "Arms", "Target_Muscles": "Triceps, Anterior Deltoids, Chest", "Sets": "3", "Reps per Set": "12-15"},
    ],
    "core": [
        {"Exercise Name": "Forearm Plank", "Execution": "Hold plank on forearms with body in straight line, engage core throughout", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Obliques, Transverse Abdominis", "Sets": "3", "Reps per Set": "30-60 seconds"},
        {"Exercise Name": "Mountain Climbers", "Execution": "Plank position, rapidly alternate driving knees toward chest", "Main_muscle": "Core", "Target_Muscles": "Rectus Abdominis, Hip Flexors, Shoulders", "Sets": "3", "Reps per Set": "20 each side"},
        {"Exercise Name": "Bicycle Crunches", "Execution": "Lie on back, alternate touching elbow to opposite knee in pedaling motion", "Main_muscle": "Core", "Target_Muscles": "Obliques, Rectus Abdominis", "Sets": "3", "Reps per Set": "15 each side"},
    ],
    "cardio": [
        {"Exercise Name": "Burpees", "Execution": "Squat down, kick feet back to plank, perform push-up, jump up explosively", "Main_muscle": "Cardiovascular", "Target_Muscles": "Full Body", "Sets": "3", "Reps per Set": "10-15"},
        {"Exercise Name": "High Knees", "Execution": "Run in place driving knees to chest height at maximum pace", "Main_muscle": "Cardiovascular", "Target_Muscles": "Core, Hip Flexors, Calves", "Sets": "3", "Reps per Set": "30 seconds"},
        {"Exercise Name": "Jumping Jacks", "Execution": "Jump spreading legs wide while raising arms overhead, return to start", "Main_muscle": "Cardiovascular", "Target_Muscles": "Full Body, Calves, Shoulders", "Sets": "3", "Reps per Set": "30 seconds"},
    ],
    "mobility": [
        {"Exercise Name": "World's Greatest Stretch", "Execution": "Lunge forward, place opposite hand on floor, rotate torso and reach skyward", "Main_muscle": "Mobility", "Target_Muscles": "Hip Flexors, Thoracic Spine, Hamstrings", "Sets": "2", "Reps per Set": "5 each side"},
        {"Exercise Name": "Deep Squat Hold", "Execution": "Lower into deep squat, hold at bottom with chest tall, gently shift weight side to side", "Main_muscle": "Mobility", "Target_Muscles": "Hips, Ankles, Lower Back", "Sets": "2", "Reps per Set": "30 seconds"},
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Muscle Split Templates
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MUSCLE_SPLITS = {
    1: [["chest", "back", "legs", "core"]],
    2: [["chest", "back", "shoulders"], ["legs", "arms", "core"]],
    3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
    4: [["chest", "shoulders"], ["back", "core"], ["legs"], ["arms", "cardio"]],
    5: [["chest"], ["back"], ["legs"], ["shoulders", "arms"], ["core", "cardio"]],
    6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms", "core"], ["cardio"]],
    7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["cardio"]],
}

DAY_LABELS = {
    1: ["Full Body"],
    2: ["Upper Body", "Lower Body"],
    3: ["Push", "Pull", "Legs"],
    4: ["Chest & Shoulders", "Back & Core", "Legs", "Arms & Cardio"],
    5: ["Chest", "Back", "Legs", "Shoulders & Arms", "Core & Cardio"],
    6: ["Chest", "Back", "Shoulders", "Legs", "Arms & Core", "Cardio"],
    7: ["Chest", "Back", "Shoulders", "Legs", "Arms", "Core", "Cardio"],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Intelligent Selection Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _select_pool(location: str) -> dict:
    """Select gym or home exercises based on workoutLocation."""
    if location.lower() in ("home", "bodyweight", "none", "no equipment", "outdoor"):
        return HOME_EXERCISES
    return GYM_EXERCISES


def _exercises_per_muscle(level: str) -> int:
    """Number of exercises per muscle group based on experienceLevel."""
    lvl = level.lower()
    if lvl == "beginner":
        return 1
    elif lvl == "intermediate":
        return 2
    return 3


def _adjust_volume(exercises: list, level: str, bmi_category: str) -> list:
    """Adjust sets and reps based on experienceLevel and BMI category."""
    lvl = level.lower()
    is_obese = bmi_category.startswith("Obesity")
    adjusted = []

    for ex in exercises:
        ex_copy = dict(ex)
        sets = int(ex_copy["Sets"])

        if lvl == "beginner":
            ex_copy["Sets"] = str(max(2, sets - 1))
        elif lvl == "advanced" and not is_obese:
            ex_copy["Sets"] = str(min(6, sets + 1))

        if is_obese and lvl == "beginner":
            ex_copy["Sets"] = str(max(1, int(ex_copy["Sets"]) - 1))

        adjusted.append(ex_copy)

    return adjusted


def _needs_extra_cardio(goal: str, bmi_category: str) -> bool:
    """Determine if extra cardio should be appended to each day."""
    goal_lower = goal.lower().replace(" ", "_")
    fat_loss_goals = ("lose_weight", "fat_loss", "cut", "weight_loss", "lean")
    if goal_lower in fat_loss_goals:
        return True
    if bmi_category in ("Overweight", "Obesity Class I", "Obesity Class II", "Obesity Class III"):
        return True
    return False


def _needs_mobility(bmi_category: str, level: str) -> bool:
    """Obese users or beginners benefit from mobility work."""
    return bmi_category.startswith("Obesity") or level.lower() == "beginner"


def _build_goal_split_override(goal: str, bmi_category: str, days: int) -> list:
    """For underweight users focused on muscle gain, bias toward strength splits."""
    goal_lower = goal.lower().replace(" ", "_")

    if bmi_category == "Underweight" and goal_lower in ("gain_muscle", "bulk", "muscle_gain", "build_muscle"):
        strength_splits = {
            1: [["chest", "back", "legs"]],
            2: [["chest", "back", "shoulders"], ["legs", "arms"]],
            3: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"]],
            4: [["chest"], ["back", "shoulders"], ["legs"], ["arms", "core"]],
            5: [["chest"], ["back"], ["legs"], ["shoulders"], ["arms", "core"]],
            6: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"]],
            7: [["chest"], ["back"], ["shoulders"], ["legs"], ["arms"], ["core"], ["chest", "back"]],
        }
        return strength_splits.get(days, None)

    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Workout Plan Generator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_workout_plan(user: UserInput, bmi_category: str) -> dict:
    """Generate a day-grouped workout plan based on user profile and BMI."""
    pool = _select_pool(user.workoutLocation)
    days = max(1, min(7, user.workoutDays))
    per_muscle = _exercises_per_muscle(user.experienceLevel)
    add_cardio = _needs_extra_cardio(user.fitnessGoal, bmi_category)
    add_mobility = _needs_mobility(bmi_category, user.experienceLevel)

    # Check for goal-specific split overrides
    override = _build_goal_split_override(user.fitnessGoal, bmi_category, days)
    split = override if override else MUSCLE_SPLITS.get(days, MUSCLE_SPLITS[3])
    labels = DAY_LABELS.get(days, DAY_LABELS[3])

    seen_exercises = set()
    workout_plan = {}

    for i, day_muscles in enumerate(split):
        day_key = "Day " + str(i + 1) + " - " + labels[i] if i < len(labels) else "Day " + str(i + 1)
        day_exercises = []

        for muscle in day_muscles:
            available = pool.get(muscle, [])
            count = 0
            for ex in available:
                if count >= per_muscle:
                    break
                if ex["Exercise Name"] not in seen_exercises:
                    day_exercises.append(dict(ex))
                    seen_exercises.add(ex["Exercise Name"])
                    count += 1

        # Adjust volume for level and BMI
        day_exercises = _adjust_volume(day_exercises, user.experienceLevel, bmi_category)

        # Add cardio for fat-loss goals or overweight/obese users
        if add_cardio and "cardio" not in day_muscles:
            cardio_pool = pool.get("cardio", [])
            for c in cardio_pool:
                if c["Exercise Name"] not in seen_exercises:
                    day_exercises.append(dict(c))
                    seen_exercises.add(c["Exercise Name"])
                    break

        # Add mobility for obese or beginner users
        if add_mobility:
            mobility_pool = pool.get("mobility", [])
            for m in mobility_pool:
                if m["Exercise Name"] not in seen_exercises:
                    day_exercises.append(dict(m))
                    seen_exercises.add(m["Exercise Name"])
                    break

        # Guarantee at least 3 exercises per day
        if len(day_exercises) < 3:
            for fallback_group in ["legs", "core", "chest", "back"]:
                for ex in pool.get(fallback_group, []):
                    if ex["Exercise Name"] not in seen_exercises:
                        day_exercises.append(dict(ex))
                        seen_exercises.add(ex["Exercise Name"])
                    if len(day_exercises) >= 3:
                        break
                if len(day_exercises) >= 3:
                    break

        workout_plan[day_key] = day_exercises

    return workout_plan


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orchestrator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_plan(user: UserInput) -> dict:
    """Generate the complete fitness plan: BMI + day-grouped workouts."""
    bmi = calculate_bmi(user.weight, user.height)
    bmi_category = get_bmi_category(bmi)
    workout_plan = generate_workout_plan(user, bmi_category)

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "workout_plan": workout_plan,
    }
