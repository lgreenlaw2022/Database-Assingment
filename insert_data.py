from db_session import session
import random
from datetime import datetime, timedelta, time
from faker import Faker
from faker_food import FoodProvider


from init_db import (
    User,
    HealthMetric,
    SleepLog,
    Food,
    FoodLog,
    UserWorkout,
    WorkoutLog,
    WorkoutRecommendation,
    Goal,
)

# Create a Faker instance
fake = Faker()
fake.add_provider(FoodProvider)

# Create 100 users
for _ in range(25):
    name = fake.name()
    age = random.randint(18, 60)
    user = User(
        name=name,
        age=age,
        # TODO: change this to a number
        gender=random.choice(["Male", "Female", "Nonbinary"]),
        weight=random.uniform(80.0, 100.0),
        height=random.uniform(150.0, 200.0),  # cm
        email=f"{name.replace(' ', '').lower()}{age}@example.com",
        password=fake.password(),
    )
    session.add(user)

# add foods because they are user independent
# make sure all of the generated entries are unique
vegetables = set()
while len(vegetables) < 12:
    vegetables.add(fake.vegetable())
fruits = set()
while len(fruits) < 12:
    fruits.add(fake.fruit())
dishes = set()
while len(dishes) < 36:
    dishes.add(fake.dish())

# Now you can use the `vegetables` and `dishes` sets in your code
for _ in range(60):  # add 60 foods to the database
    category = random.randint(1, 5)
    if category == 5:  # 1/5 of the time, category is fruit
        if not fruits:  # If the set is empty, skip to the next iteration
            continue
        name = fruits.pop()  # Use a unique fruit
    elif category == 4:  # 1/5 of the time, category is vegetable
        if not vegetables:  # If the set is empty, skip to the next iteration
            continue
        name = vegetables.pop()  # Use a unique vegetable
    else:
        if not dishes:  # If the set is empty, skip to the next iteration
            continue
        name = dishes.pop()  # Use a unique dish

    food = Food(
        name=name,
        calories=random.randint(50, 700),  # Calories between 50 and 500
        category=category,
    )
    session.add(food)

# Create dummy data for the WorkoutRecommendation table
# TODO: make consistent through the whole file?
exercise_types = [1, 2, 3]  # 1 = cardio, 2 = strength, 3 = flexibility
difficulty_levels = [1, 2, 3]  # 1 = easy, 2 = medium, 3 = hard

for _ in range(50):  # Create 50 workout recommendations
    workout_recommendation = WorkoutRecommendation(
        exercise_type=random.choice(exercise_types),
        workout_name=(f"Workout {_}"),
        description=fake.sentence(),
        duration=random.uniform(0.05, 2.0),  # hours
        difficulty_level=random.choice(difficulty_levels),
    )
    session.add(workout_recommendation)

# Commit the users, food, workout recommendations to the database
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
        sleep = SleepLog(
            user_id=user.id,
            duration=hours,
            quality=random.randint(1, 4),  # Quality between 1 (poor) and 4 (excellent)
            start_time=start_time.time(),
            end_time=end_time.time(),
            date=start_time.date(),
        )
        session.add(sleep)

    # TODO: make a number?

    # Create dummy data for FoodLog table
    for day in range(30):  # For each day in a 30-day window
        # for user in session.query(User).all():
        for _ in range(3):  # Add 3 entries each day
            food = random.choice(session.query(Food).all())
            food_log_date = start_date + timedelta(days=day)
            food_log = FoodLog(
                user_id=user.id,
                food_id=food.id,
                date=food_log_date,
                time=fake.time_object(),
            )
            session.add(food_log)

    # Create dummy data for the UserWorkout and WorkoutLog tables
    # TODO: maybe I should change the insertions to just have the same description, rather than the fake sentence
    workout_recommendations = session.query(WorkoutRecommendation).all()
    # Get the current date
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    # Create dummy data for the UserWorkout and WorkoutLog tables
    for i in range(30):  # Each user has 30 workouts
        # Calculate the date of the workout by backdating i days from today
        workout_date = start_date + timedelta(days=i)

        # 30% of the time, use a workout recommendation
        if random.random() < 0.3 and workout_recommendations:
            workout_recommendation = random.choice(workout_recommendations)
            workout_log = WorkoutLog(
                user_id=user.id,
                recommendation_id=workout_recommendation.id,
                calories_burned=random.uniform(
                    100.0, 500.0
                ),  # Calories burned between 100 and 500
                heart_rate=random.randint(60, 250),  # Heart rate between 60 and 250
                date=workout_date,
            )
        else:
            # User creates a workout and logs it immediately
            user_workout = UserWorkout(
                exercise_type=random.choice(exercise_types),
                description=fake.sentence(),
                duration=random.uniform(0.05, 2.0),  # hours
                difficulty_level=random.choice(difficulty_levels),
            )
            session.add(user_workout)
            session.commit()

            workout_log = WorkoutLog(
                user_id=user.id,
                user_workout_id=user_workout.id,
                calories_burned=random.uniform(
                    100.0, 500.0
                ),  # Calories burned between 100 and 500
                heart_rate=random.randint(60, 250),  # Heart rate between 60 and 250
                date=workout_date,
            )
        session.add(workout_log)

    # Create dummy data for the Goal table
    # TODO: probably should move this to the top of the file
    goal_types = [1, 2, 3]  # 1 = sleep, 2 = nutrition, 3 = workout

    for _ in range(2):  # Each user has 52 goals
        start_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
        end_date = start_date + timedelta(
            days=random.randint(7, 30)
        )  # Goal lasts between 14 and 30 days
        goal_type = random.choice(goal_types)
        goal = Goal(
            user_id=user.id,
            description=(f"Goal {_}, type {goal_type}"),
            start_date=start_date,
            end_date=end_date,
            goal_type=goal_type,
        )
        session.add(goal)

# Commit the dummy data to the database
# TODO: explain why I am only committing once at the end
session.commit()
