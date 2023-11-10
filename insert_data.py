from db_session import session
from faker import Faker
import random
from datetime import datetime, timedelta, time

from init_db import (
    engine,
    User,
    HealthMetric,
    Sleep,
    # Food,
    # NutritionLog,
    # UserWorkout,
    # WorkoutLog,
    # WorkoutRecommendation,
    # Goal,
)

# Create a Faker instance
fake = Faker()

# Create 100 users
for _ in range(50):
    name = fake.name()
    age = random.randint(18, 60)
    user = User(
        name=name,
        age=age,
        gender=random.choice(["Male", "Female", "Nonbinary"]),
        weight=random.uniform(80.0, 100.0),
        height=random.uniform(150.0, 200.0),  # cm
        email=f"{name.replace(' ', '').lower()}{age}@example.com",
        password=fake.password(),
    )
    session.add(user)

# Commit the users to the database
session.commit()

# Create dummy data for other tables
for user in session.query(User).all():
    start_date = datetime.now() - timedelta(days=30)  # 30 days ago
    end_date = datetime.now()  # today

    delta = timedelta(days=1)  # increment by one day
    current_date = start_date
    while current_date <= end_date:
        random_time = (
            datetime.now()
            .replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            .time()
        )
        timestamp = datetime.combine(current_date.date(), random_time)
        health_metric = HealthMetric(
            user_id=user.id,
            # this heart rate is resting heart rate only because the workout logs provide the working out heart rate
            heart_rate=random.randint(40, 130),
            steps_taken=random.randint(0, 20000),
            stand_hours=random.randint(0, 20),
            systolic_bp=random.randint(90, 130),
            diastolic_bp=random.randint(20, 90),
            timestamp=timestamp,
        )
        session.add(health_metric)
        current_date += delta

    #     # TODO: comments
    # add sleep data
    # TODO: make all of the data time population the same
    # TODO: move to top for reuse
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    for _ in range(30):  # Each user has 60 sleep records (one a day)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(
            days=_,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        hours = round(
            random.uniform(3, 13), 2
        )  # Duration in hours rounded to 100ths place
        end_time = start_time + timedelta(hours=hours)
        sleep = Sleep(
            user_id=user.id,
            duration=hours,
            quality=random.randint(1, 4),  # Quality between 1 (poor) and 4 (excellent)
            start_time=start_time.time(),
            end_time=end_time.time(),
            date=start_time.date(),
        )
        session.add(sleep)

#     # Create dummy data for the Food and NutritionLog tables
#     # TODO: make a number?
#     food_categories = ["Protein", "Carb", "Fat", "Veggie", "Fruit"]

#     for _ in range(100):  # Each user has 100 different foods
#         food = Food(
#             user_id=user.id,
#             name=fake.word(),  # TODO: this needs to be better
#             calories=random.randint(50, 700),  # Calories between 50 and 500
#             category=random.choice(food_categories),
#         )
#         session.add(food)

#     for _ in range(
#         365  # TODO: this doesn't actually guarantee that there's an entry for each day I think
#     ):  # Each user has 365 nutrition logs (one for each day of the year)
#         food = random.choice(session.query(Food).filter(Food.user_id == user.id).all())
#         nutrition_log = NutritionLog(
#             user_id=user.id,
#             food_id=food.id,
#             date=fake.date_between(start_date="-1y", end_date="today"),
#             time=fake.time_object(),
#         )
#         session.add(nutrition_log)

#     # Create dummy data for the WorkoutRecommendation table
#     exercise_types = [1, 2, 3]  # 1 = cardio, 2 = strength, 3 = flexibility
#     difficulty_levels = [1, 2, 3]  # 1 = easy, 2 = medium, 3 = hard
#     workout_names = ["Workout A", "Workout B", "Workout C", "Workout D", "Workout E"]

#     for _ in range(100):  # Create 100 workout recommendations
#         workout_recommendation = WorkoutRecommendation(
#             exercise_type=random.choice(exercise_types),
#             workout_name=random.choice(workout_names),
#             description=fake.sentence(),
#             duration=random.uniform(0.5, 2.0),  # Duration between 0.5 and 2 hours
#             difficulty_level=random.choice(difficulty_levels),
#         )
#         session.add(workout_recommendation)

#     # Create dummy data for the UserWorkout and WorkoutLog tables
#     for _ in range(365):  # Each user has 365 workouts (one for each day of the year)
#         user_workout = UserWorkout(
#             user_id=user.id,
#             exercise_type=random.choice(exercise_types),
#             description=fake.sentence(),
#             duration=random.uniform(0.15, 2.0),  # Duration between 0.15 and 2 hours
#             difficulty_level=random.choice(difficulty_levels),
#         )
#         session.add(user_workout)

#     user_workouts = (
#         session.query(UserWorkout).filter(UserWorkout.user_id == user.id).all()
#     )
#     workout_recommendations = session.query(WorkoutRecommendation).all()

#     for _ in range(
#         365
#     ):  # Each user has 365 workout logs (one for each day of the year)
#         # 30% of the time, use a workout recommendation
#         if random.random() < 0.3 and workout_recommendations:
#             workout_recommendation = random.choice(workout_recommendations)
#             workout_log = WorkoutLog(
#                 user_id=user.id,
#                 workout_recommendation_id=workout_recommendation.id,
#                 calories_burned=random.uniform(
#                     100.0, 500.0
#                 ),  # Calories burned between 100 and 500
#                 heart_rate=random.randint(60, 250),  # Heart rate between 60 and 250
#                 date=fake.date_between(start_date="-1y", end_date="today"),
#             )
#         else:
#             user_workout = random.choice(user_workouts)
#             workout_log = WorkoutLog(
#                 user_id=user.id,
#                 user_workout_id=user_workout.id,
#                 calories_burned=random.uniform(
#                     100.0, 500.0
#                 ),  # Calories burned between 100 and 500
#                 heart_rate=random.randint(60, 250),  # Heart rate between 60 and 250
#                 date=fake.date_between(start_date="-1y", end_date="today"),
#             )
#         session.add(workout_log)

#     # Create dummy data for the Goal table
#     goal_types = [1, 2, 3]  # 1 = sleep, 2 = nutrition, 3 = workout

#     for _ in range(5):  # Each user has 5 goals
#         start_date = fake.date_between(start_date="-1y", end_date="today")
#         end_date = start_date + timedelta(
#             days=random.randint(14, 90)
#         )  # Goal lasts between 14 and 90 days
#         goal = Goal(
#             user_id=user.id,
#             description=fake.sentence(),
#             start_date=start_date,
#             end_date=end_date,
#             goal_type=random.choice(goal_types),
#         )
#         session.add(goal)

# Commit the dummy data to the database
session.commit()
