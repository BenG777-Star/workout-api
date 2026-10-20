from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from models import CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)
    workouts = fields.List(
        fields.Nested(lambda: WorkoutSchema(only=('id', 'date', 'duration_minutes'))),
        dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True,
                                  validate=validate.Range(min=1, max=1440))
    notes = fields.Str(load_default=None, allow_none=True,
                       validate=validate.Length(max=500))
    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema(exclude=('workout_id',))),
        dump_only=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(load_default=None, allow_none=True, strict=True,
                      validate=validate.Range(min=0))
    sets = fields.Int(load_default=None, allow_none=True, strict=True,
                      validate=validate.Range(min=0))
    duration_seconds = fields.Int(load_default=None, allow_none=True, strict=True,
                                  validate=validate.Range(min=0))
    exercise = fields.Nested(ExerciseSchema(only=('id', 'name', 'category')),
                             dump_only=True)

    @validates_schema
    def validate_metrics(self, data, **kwargs):
        has_reps_sets = data.get('reps') is not None and data.get('sets') is not None
        has_duration = data.get('duration_seconds') is not None
        if not (has_reps_sets or has_duration):
            raise ValidationError(
                'Provide both reps and sets, or a duration_seconds.', 'reps')


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts',))
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()