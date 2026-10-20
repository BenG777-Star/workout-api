from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()

CATEGORIES = ['strength', 'cardio', 'flexibility', 'balance', 'other']


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # TABLE CONSTRAINTS
    __table_args__ = (
        db.CheckConstraint('length(name) > 0', name='ck_exercise_name_not_empty'),
    )

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise',
        cascade='all, delete-orphan')
    workouts = association_proxy(
        'workout_exercises', 'workout',
        creator=lambda w: WorkoutExercise(workout=w))

    # MODEL VALIDATIONS
    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Exercise name must be a non-empty string.')
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        if value not in CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(CATEGORIES)}.')
        return value

    def __repr__(self):
        return f'<Exercise {self.id} {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # TABLE CONSTRAINT
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout',
        cascade='all, delete-orphan')
    exercises = association_proxy(
        'workout_exercises', 'exercise',
        creator=lambda e: WorkoutExercise(exercise=e))

    # MODEL VALIDATIONS
    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError('duration_minutes must be a positive integer.')
        return value

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('date must be a valid date.')
        return value

    def __repr__(self):
        return f'<Workout {self.id} {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # TABLE CONSTRAINTS
    __table_args__ = (
        db.UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise'),
        db.CheckConstraint('reps IS NULL OR reps >= 0', name='ck_we_reps_nonneg'),
        db.CheckConstraint('sets IS NULL OR sets >= 0', name='ck_we_sets_nonneg'),
        db.CheckConstraint('duration_seconds IS NULL OR duration_seconds >= 0',
                           name='ck_we_duration_nonneg'),
    )

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # MODEL VALIDATION
    @validates('reps', 'sets', 'duration_seconds')
    def validate_non_negative(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f'{key} must be a non-negative integer.')
        return value

    def __repr__(self):
        return f'<WorkoutExercise w={self.workout_id} e={self.exercise_id}>'