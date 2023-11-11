from init_db import (
    User,
    HealthMetric,
    Sleep,
    Food,
    FoodLog,
    UserWorkout,
    WorkoutRecommendation,
)
from sqlalchemy import func
from db_session import session
from faker import Faker
import random
from datetime import datetime, timedelta

# initialize Faker for transaction demonstrations
fake = Faker()
# TODO: switch to this global?
# Get the date 30 days ago
start_date_30 = datetime.now() - timedelta(days=30)

# TODO: make sure I am taking advantage of the back ref relationships
# Inserting a new user
# TODO: maybe make the indexes for these queries because its hard to get a user
new_user = User(
    name="Libby Greenlaw",
    age=18,
    gender="Female",
    weight=130,
    height=170,
    email="libbygreenlaw18@example.com",
    password=fake.password(),
)
session.add(new_user)
session.commit()
print(
    f"\nadded user: Name: {new_user.name}, Age: {new_user.age}, Email: {new_user.email}"
)

print("New User Count after insertion:")
user_count = session.query(func.count(User.id)).scalar()
print(user_count)

libby = new_user


# HEALTH_METRIC TABLE QUERIES

# Add health metrics for libby
# TODO: hardcode some so that we can tell it is correct
health_metric = HealthMetric(
    user_id=libby.id,
    heart_rate=75,
    steps_taken=7000,
    stand_hours=10,
    systolic_bp=random.randint(90, 130),
    diastolic_bp=random.randint(20, 90),
    timestamp=datetime.now(),
)
session.add(health_metric)
session.commit()

# Get the last health metric for libby
last_metric = (
    session.query(HealthMetric)
    .filter(HealthMetric.user_id == libby.id)
    .order_by(HealthMetric.timestamp.desc())
    .first()
)

if last_metric:
    print(f"\nLast health metric for {libby.name}:")
    print(
        f"Heart Rate: {last_metric.heart_rate}, Steps Taken: {last_metric.steps_taken}, Stand Hours: {last_metric.stand_hours}, Systolic BP: {last_metric.systolic_bp}, Diastolic BP: {last_metric.diastolic_bp}"
    )
else:
    print("No health metrics found for this user.")


# SLEEP TABLE QUERIES
# add a sleep record for libby
start_datetime = datetime.combine(datetime.today(), datetime.now().time())
duration = 8
end_datetime = start_datetime + timedelta(hours=duration)
end_time = end_datetime.time()

sleep = Sleep(
    user_id=libby.id,
    duration=8,
    quality=4,
    start_time=start_datetime.time(),
    end_time=end_time,
    date=datetime.now().date(),
)
session.add(sleep)
session.commit()

# Get the last sleep record for libby
last_sleep = (
    session.query(Sleep)
    .filter(Sleep.user_id == libby.id)  # TODO: necessary?
    .order_by(Sleep.date.desc())
    .first()
)

if last_sleep:
    print(f"\nLast sleep record for {libby.name}:")
    print(
        f"Date: {last_sleep.date} \nDuration: {last_sleep.duration}, Quality: {last_sleep.quality}, Start Time: {last_sleep.start_time}, End Time: {last_sleep.end_time}"
    )


### delete record
# delete user
# update user info

# FOOD TABLES Transactions
# Add a food to the Food table
food = Food(name="Test Food", calories=95, category=1)
session.add(food)
session.commit()  # Commit the transaction to get the id of the new Food object

# Check if the food is already in user 1's log
existing_food_log = (
    session.query(FoodLog)
    .join(Food)
    .filter(FoodLog.user_id == 1, Food.id == food.id)
    .first()
)
if existing_food_log is None:
    # If the food is not in the log, add it
    food_log = FoodLog(
        user_id=1,
        food_id=food.id,
        date=datetime.now().date(),
        time=datetime.now().time(),
    )
    session.add(food_log)
    session.commit()
else:
    print("This food is already in the user's log.")


# Specify the user_id and food_id
user_id = 1  # Replace with the actual user_id
food_id = (
    food.id
)  # Replace with the actual food_id, use the one I just added? otherwise need to select one

# Find the food log entry
food_log = (
    session.query(FoodLog)
    .filter(FoodLog.user_id == user_id, FoodLog.food_id == food_id)
    .first()
)

if food_log is not None:
    # If the food log entry exists, delete it
    session.delete(food_log)
    session.commit()
    print("The food log entry has been deleted.")
else:
    print("No matching food log entry was found.")

# Specify the food_id and new_calories
food_id = 1  # Replace with the actual food_id
new_calories = 100  # Replace with the new calories

# Find the food
food = session.query(Food).filter(Food.id == food_id).first()

if food is not None:
    # If the food exists, update its calories
    food.calories = new_calories
    session.commit()
    print("The calories of the food have been updated.")
else:
    print("No matching food was found.")

# add entry to recommended workouts
workout_recommendation = WorkoutRecommendation(
    exercise_type=1,
    workout_name="Test Workout",
    description="Test workout description",
    duration=0.5,  # hours
    difficulty_level=1,
)
session.add(workout_recommendation)
session.commit()
# Check if the new WorkoutRecommendation object was successfully added to the table
if workout_recommendation.id is not None:
    print("The new WorkoutRecommendation entry was successfully added to the table.")
else:
    print("The new WorkoutRecommendation entry was not added to the table.")

# Update the name of a WorkoutRecommendation entry
workout_to_update = workout_recommendation.id
if workout_to_update is not None:
    workout_to_update.name = "Updated Workout Name"
    session.commit()
    print("A WorkoutRecommendation entry was successfully updated.")
else:
    print("No WorkoutRecommendation entry was found to update.")

# Delete a WorkoutRecommendation entry
workout_to_delete = workout_recommendation.id
if workout_to_delete is not None:
    session.delete(workout_to_delete)
    session.commit()
    print("A WorkoutRecommendation entry was successfully deleted.")
else:
    print("No WorkoutRecommendation entry was found to delete.")

# add entry to user workouts
user_workout = UserWorkout(
    exercise_type=1,
    description="test user workout",
    duration=0.5,  # hours
    difficulty_level=1,
)
session.add(user_workout)
session.commit()
# Check if the new UserWorkout object was successfully added to the table
if user_workout.id is not None:
    print("The new UserWorkout entry was successfully added to the table.")
else:
    print("The new UserWorkout entry was not added to the table.")


# TODO: check that only one of the workout FK exist for the workout log entries
