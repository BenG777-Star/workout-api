from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (exercise_schema, exercises_schema, workout_schema,
                     workouts_schema, workout_exercise_schema)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)


def respond(body, status=200):
    return make_response(body, status)


def err(message, status):
    return respond({'error': message}, status)


def load_json(schema):
    """Return (data, None) or (None, error_response)."""
    payload = request.get_json(silent=True)
    if payload is None:
        return None, err('Request body must be valid JSON.', 400)
    try:
        return schema.load(payload), None
    except ValidationError as e:
        return None, respond({'errors': e.messages}, 422)


def commit_or_error():
    try:
        db.session.commit()
        return None
    except IntegrityError as e:
        db.session.rollback()
        return err(f'Database constraint violated: {e.orig}', 409)


# ---------- Workouts ----------
@app.get('/workouts')
def get_workouts():
    return respond(workouts_schema.dump(Workout.query.all()))


@app.get('/workouts/<int:id>')
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return err('Workout not found', 404)
    return respond(workout_schema.dump(workout))


@app.post('/workouts')
def create_workout():
    data, error = load_json(workout_schema)
    if error:
        return error
    try:
        workout = Workout(**data)
    except ValueError as e:
        return err(str(e), 422)
    db.session.add(workout)
    error = commit_or_error()
    if error:
        return error
    return respond(workout_schema.dump(workout), 201)


@app.delete('/workouts/<int:id>')
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return err('Workout not found', 404)
    db.session.delete(workout)  # cascades to WorkoutExercises
    db.session.commit()
    return respond({}, 204)


# ---------- Exercises ----------
@app.get('/exercises')
def get_exercises():
    return respond(exercises_schema.dump(Exercise.query.all()))


@app.get('/exercises/<int:id>')
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return err('Exercise not found', 404)
    return respond(exercise_schema.dump(exercise))


@app.post('/exercises')
def create_exercise():
    data, error = load_json(exercise_schema)
    if error:
        return error
    try:
        exercise = Exercise(**data)
    except ValueError as e:
        return err(str(e), 422)
    db.session.add(exercise)
    error = commit_or_error()
    if error:
        return error
    return respond(exercise_schema.dump(exercise), 201)


@app.delete('/exercises/<int:id>')
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return err('Exercise not found', 404)
    db.session.delete(exercise)  # cascades to WorkoutExercises
    db.session.commit()
    return respond({}, 204)


# ---------- Add exercise to workout ----------
@app.post('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises')
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if not workout:
        return err('Workout not found', 404)
    if not exercise:
        return err('Exercise not found', 404)

    data, error = load_json(workout_exercise_schema)
    if error:
        return error
    try:
        we = WorkoutExercise(workout=workout, exercise=exercise, **data)
    except ValueError as e:
        db.session.rollback()
        return err(str(e), 422)
    db.session.add(we)
    error = commit_or_error()
    if error:
        return error
    return respond(workout_exercise_schema.dump(we), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)