# FitLife AI – Fitness & Nutrition Planner API

AI-powered fitness and nutrition planning API built with FastAPI, using real Kaggle datasets.

## Datasets
- **Gym Exercises**: 617 exercises from [rishitmurarka/gym-exercises-dataset](https://www.kaggle.com/datasets/rishitmurarka/gym-exercises-dataset)
- **Nutrition Meals**: 1,698 meal plans from [bitanianielsen/nutrition-daily-meals-in-diseases-cases](https://www.kaggle.com/datasets/bitanianielsen/nutrition-daily-meals-in-diseases-cases)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate-plan` | Generate full workout + diet plan |
| POST | `/bmi` | Calculate BMI |
| GET | `/health` | Health check |
| GET | `/dataset-info` | Dataset metadata |
| GET | `/docs` | Swagger UI |

## Example Request

```bash
curl -X POST https://YOUR-URL/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "age": 22,
    "gender": "male",
    "weight": 75,
    "height": 1.75,
    "goal": "muscle gain",
    "workout_days": 4,
    "level": "beginner",
    "equipment": "home",
    "dietary_preference": "none"
  }'
```

## Tech Stack
- FastAPI + Uvicorn
- pandas + scikit-learn (cosine similarity)
- Pydantic validation
