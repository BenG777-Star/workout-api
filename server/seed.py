#!/usr/bin/env python3

from datetime import date

from app import app
from models import *

with app.app_context():
    print('Clearing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print('Seeding exercises...')
    squat = Exercise(name='Squat', category='strength', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='strength', equipment_needed=False)
    run = Exercise(name='Running', category='cardio', equipment_needed=False)
    plank = Exercise(name='Plank', category='balance', equipment_needed=False)
    stretch = Exercise(name='Hamstring Stretch', category='flexibility',
                       equipment_needed=False)
    db.session.add_all([squat, pushup, run, plank, stretch])

    print('Seeding workouts...')
    w1 = Workout(date=date(2026, 10, 12), duration_minutes=45, notes='Leg day')
    w2 = Workout(date=date(2026, 10, 14), duration_minutes=30, notes='Cardio + core')
    w3 = Workout(date=date(2026, 10, 16), duration_minutes=20, notes='Mobility')
    db.session.add_all([w1, w2, w3])
    db.session.commit()

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=w1, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=w2, exercise=run, duration_seconds=1200),
        WorkoutExercise(workout=w2, exercise=plank, duration_seconds=180),
        WorkoutExercise(workout=w3, exercise=stretch, duration_seconds=300),
        WorkoutExercise(workout=w3, exercise=plank, duration_seconds=120),
    ])
    db.session.commit()
    print('Done!')