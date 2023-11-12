from db_session import session
import random
from datetime import datetime, timedelta
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

# TODO: comments, explain ACID
# Note that 3-4 seconds of the file run time is due to instantiating the faker module.
fake = Faker()
# Add the Faker FoodProvider to the Faker instance
fake.add_provider(FoodProvider)

### INSERT USERS ###
genders = [1, 2, 3]  # M, F, NonBinary
for _ in range(25):  # add 25 users
    name = fake.name()
    age = random.randint(18, 70)
    user = User(
        name=name,
        age=age,
        gender=random.choice(genders),
        weight=random.uniform(80.0, 100.0),  # kg
        height=random.uniform(150.0, 200.0),  # cm
        email=f"{name.replace(' ', '').lower()}{age}@example.com",
        password=fake.password(),  # faker library gives a hashed password
    )
    session.add(user)
session.commit()

### INSERT FOODS ### (user independent)
# set() makes sure all of the generated entries (food names) are unique
vegetables = set()
while len(vegetables) < 12:
    vegetables.add(fake.vegetable())
fruits = set()
while len(fruits) < 12:
    fruits.add(fake.fruit())
dishes = set()
while len(dishes) < 36:
    # faked dishes are not aligned with the food categories
    # but this is the closest real data approximation
    dishes.add(fake.dish())

for _ in range(60):  # add 60 foods to the database
    category = random.randint(1, 5)
    if category == 5:  # 1/5 of the time, category is fruit
        if not fruits:  # If the set is empty, skip to the next iteration
            continue
        name = fruits.pop()  # unique fruit
    elif category == 4:  # 1/5 of the time, category is vegetable
        if not vegetables:  # If the set is empty, skip to the next iteration
            continue
        name = vegetables.pop()  # unique vegetable
    else:
        if not dishes:  # If the set is empty, skip to the next iteration
            continue
        name = dishes.pop()  # unique dish (no fakers for the other food types)

    food = Food(
        name=name,
        calories=random.randint(50, 700),  # Calories between 50 and 700
        category=category,
    )
    session.add(food)
session.commit()

### INSERT WORKOUT RECOMMENDATIONS ### (user independent)
exercise_types = [1, 2, 3]  # 1 = cardio, 2 = strength, 3 = flexibility
difficulty_levels = [1, 2, 3]  # 1 = easy, 2 = medium, 3 = hard

for i in range(50):  # Create 50 workout recommendations
    workout_recommendation = WorkoutRecommendation(
        exercise_type=random.choice(exercise_types),
        workout_name=(f"Workout {i}"),
        description=fake.sentence(),
        duration=random.uniform(0.05, 2.0),  # hours
        difficulty_level=random.choice(difficulty_levels),
    )
    session.add(workout_recommendation)
session.commit()


# frequently used insertion start date, backdated 30 days
start_date_30 = datetime.now() - timedelta(days=30)

# Create dummy data for other tables with user FKs
"""
I have separated the insertions out into different loops over the user list
This helps make my code more readable and helps me commit the data to the database
in the correct order and as soon as the table is filled. This helps in the case 
of a rollback or computer crash. This choice comes at the cost of run time performance. 
In practice the data would not be inserted like this (decreased insertion time).
"""
### Insert data for HealthMetric table ###
for user in session.query(User).all():
    end_date = datetime.now()  # today
    delta = timedelta(days=1)  # increment by one day
    current_date = start_date_30
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
            # this heart rate is resting heart rate only (workout log provides active heart rate)
            heart_rate=random.randint(40, 120),
            steps_taken=random.randint(0, 20000),
            stand_hours=random.randint(0, 20),
            systolic_bp=random.randint(90, 130),
            diastolic_bp=random.randint(20, 90),
            timestamp=timestamp,
        )
        session.add(health_metric)
        current_date += delta  # add one entry per user per day
session.commit()

### Insert data for SleepLog table ###
for user in session.query(User).all():
    for _ in range(30):  # Each user has 60 sleep records (one a day)
        start_time = datetime.combine(start_date_30, datetime.min.time()) + timedelta(
            days=_,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        hours = round(
            random.uniform(3, 13), 2
        )  # Duration in hours rounded to 100ths place
        end_time = start_time + timedelta(hours=hours)

        # Ensure that the end_datetime is correctly calculated
        sleep = SleepLog(
            user_id=user.id,
            duration=hours,
            quality=random.randint(1, 4),  # Quality between 1 (poor) and 4 (excellent)
            start_time=start_time.time(),
            end_time=end_time.time(),
            date=start_time.date(),
        )
        session.add(sleep)
session.commit()

### Insert data for FoodLog table ###
for user in session.query(User).all():
    food_log_date = start_date_30 + timedelta(days=1)
    for day in range(30):  # For each day in a 30-day window
        for _ in range(3):  # Add 3 entries each day
            # log a random food from Food table
            food = random.choice(session.query(Food).all())
            food_log = FoodLog(
                user_id=user.id,
                food_id=food.id,
                date=food_log_date,
                time=fake.time_object(),
            )
            session.add(food_log)
        food_log_date += timedelta(days=1)  # Increment the date
session.commit()

### Insert data for WorkoutLog and UserWorkout tables ###
for user in session.query(User).all():
    workout_recommendations = session.query(WorkoutRecommendation).all()
    for i in range(30):  # Each user has 30 workouts
        # Calculate the date of the workout by backdating i days from today
        workout_date = start_date_30 + timedelta(days=i)
        # 30% of the time, use a workout recommendation
        if random.random() < 0.3 and workout_recommendations:
            workout_recommendation = random.choice(workout_recommendations)
            workout_log = WorkoutLog(
                user_id=user.id,
                recommendation_id=workout_recommendation.id,
                calories_burned=random.uniform(
                    100.0, 500.0
                ),  # Calories burned between 100 and 500
                heart_rate=random.randint(90, 250),  # Heart rate between 60 and 250
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
            # need to commit each workout so that it can be logged
            # TODO: how can I change this, doesn't align with ACID
            session.commit()

            workout_log = WorkoutLog(
                user_id=user.id,
                user_workout_id=user_workout.id,
                calories_burned=random.uniform(
                    100.0, 500.0
                ),  # Calories burned between 100 and 500
                heart_rate=random.randint(90, 250),  # Heart rate between 60 and 250
                date=workout_date,
            )
        session.add(workout_log)
session.commit()

### INSERT GOALS ###
goal_types = [1, 2, 3]  # 1 = sleep, 2 = nutrition, 3 = workout
for user in session.query(User).all():
    for i in range(2):  # Each user has 2 goals in beginning in the past month
        # get random start and end dates for goal
        start_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
        end_date = start_date + timedelta(
            days=random.randint(7, 30)
        )  # Goal lasts between 7 and 30 days
        goal_type = random.choice(goal_types)
        goal = Goal(
            user_id=user.id,
            description=(f"Goal {i}, type {goal_type}"),
            start_date=start_date,
            end_date=end_date,
            goal_type=goal_type,
        )
        session.add(goal)
session.commit()
