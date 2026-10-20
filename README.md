# Workout Tracker API

Flask + SQLAlchemy + Marshmallow backend for tracking workouts and reusable exercises.

## Setup
```
python3.8 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd server
export FLASK_APP=app.py
flask db upgrade head
python seed.py
python app.py   # runs on port 5555
```

## Models
- **Exercise**: id, name (unique), category, equipment_needed
- **Workout**: id, date, duration_minutes, notes
- **WorkoutExercise** (join): id, workout_id, exercise_id, reps, sets, duration_seconds

Deleting a workout or exercise also deletes its WorkoutExercises.

## Validations
- **Table constraints**: unique and non-null exercise name; non-empty name check; `duration_minutes > 0`; reps/sets/duration_seconds `>= 0`; unique (workout_id, exercise_id) pair.
- **Model validations**: exercise name non-empty, category in allowed list; workout duration positive and date valid; reps/sets/duration non-negative.
- **Schema validations**: required fields, length, `OneOf` category, `Range` on numbers, and a schema-level rule that a WorkoutExercise needs reps+sets or a duration.

## Endpoints
| Method | Route | Description |
|---|---|---|
| GET | /workouts | List workouts |
| GET | /workouts/<id> | Workout with its exercises (reps/sets/duration) |
| POST | /workouts | Create workout |
| DELETE | /workouts/<id> | Delete workout and its WorkoutExercises |
| GET | /exercises | List exercises |
| GET | /exercises/<id> | Exercise with associated workouts |
| POST | /exercises | Create exercise |
| DELETE | /exercises/<id> | Delete exercise and its WorkoutExercises |
| POST | /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises | Add exercise to workout |