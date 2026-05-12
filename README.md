# FitLife AI – Fitness & Nutrition Planner API

Personalized workout and diet plans via a clean FastAPI endpoint.

## Endpoints

| Method | Path             | Description                  |
|--------|------------------|------------------------------|
| GET    | `/`              | API info & available routes  |
| GET    | `/health`        | Health check                 |
| POST   | `/generate-plan` | Generate workout + diet plan |
| GET    | `/docs`          | Interactive Swagger UI       |

## Example Request

```bash
curl -X POST https://YOUR-APP.koyeb.app/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "gender": "male",
    "height": 1.78,
    "weight": 82.0,
    "fitnessGoal": "gain_muscle",
    "workout_days": 4,
    "equipment": "full_gym"
  }'
```

## Deploy on Koyeb (Free Tier)

1. Push this repo to GitHub
2. Go to [app.koyeb.com](https://app.koyeb.com)
3. **Create Web Service** → Select GitHub → Pick this repo
4. Koyeb auto-detects the Dockerfile
5. Instance: select **Eco** (free)
6. Click **Deploy**

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
