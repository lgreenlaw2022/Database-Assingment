from init_db import (
    User,
    HealthMetric,
    SleepLog,
    Food,
    FoodLog,
    WorkoutRecommendation,
    WorkoutLog,
    UserWorkout,
    Goal,
)
from sqlalchemy import func, text, desc
from db_session import session
from faker import Faker
import random
from datetime import datetime, timedelta
import time


query_start_time = time.time()
# initialize Faker for transaction demonstrations
fake = Faker()
# TODO: switch to this global?
# Get the date 30 days ago
start_date_30 = datetime.now() - timedelta(days=30)

# TODO: make sure I am taking advantage of the back ref relationships
# USER TABLE QUERIES
print("First 5 users:")
all_users = session.query(User).limit(5).all()
for user in all_users:
    print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")

print("\nTotal User Count:")
user_count = session.query(func.count(User.id)).scalar()
print(user_count)

# HEALTH_METRIC TABLE QUERIES
# TODO: review indexes for this
# Get the user with id 1
user1 = session.query(User).filter(User.id == 1).first()

if user1:
    # Get the date 30 days ago
    start_date = datetime.now() - timedelta(days=30)

    # Get average health metrics over the last 30 days
    avg_metrics = (
        session.query(
            func.avg(HealthMetric.heart_rate),
            func.avg(HealthMetric.steps_taken),
            func.avg(HealthMetric.stand_hours),
            func.avg(HealthMetric.systolic_bp),
            func.avg(HealthMetric.diastolic_bp),
        )
        .filter(
            HealthMetric.user_id == user1.id,
            HealthMetric.timestamp >= start_date,
        )
        .first()
    )

    print(f"\nAverage health metrics for {user1.name} over the last 30 days:")
    print(
        f"Heart Rate: {avg_metrics[0]}, Steps Taken: {avg_metrics[1]}, Stand Hours: {avg_metrics[2]}, Systolic BP: {avg_metrics[3]}, Diastolic BP: {avg_metrics[4]}"
    )
else:
    print("User not found.")

# Get the user with id 2
user2 = session.query(User).filter(User.id == 2).first()

if user2:
    # Get the date 7 days ago
    start_date = datetime.now() - timedelta(days=7)

    # Get average steps taken over the last 7 days
    avg_steps = (
        session.query(
            func.avg(HealthMetric.steps_taken),
        )
        .filter(
            HealthMetric.user_id == user2.id,
            HealthMetric.timestamp >= start_date,
        )
        .scalar()
    )

    print(f"\nAverage steps per day for {user2.name} over the last 7 days: {avg_steps}")
else:
    print("User not found.")

# SLEEP TABLE QUERIES
# demonstrates useful calls for sleep statistics
# NOTE: first() ensures user1 is a User object (or None) not a query object
user1 = session.query(User).filter(User.id == 1).first()

if user1:
    # Get the date 30 days ago
    start_date = datetime.now() - timedelta(days=30)
    # Get today's date
    end_date = datetime.now()

    # Get average sleep duration and quality over the last 30 days
    avg_sleep = (
        session.query(
            func.avg(SleepLog.duration),
            func.avg(SleepLog.quality),
        )
        .filter(
            SleepLog.user == user1,
            SleepLog.date.between(start_date, end_date),
        )
        .first()
    )

    print(
        f"\nAverage sleep duration and quality for {user1.name} over the last 30 days:"
    )
    print(f"Duration: {avg_sleep[0]}, Quality: {avg_sleep[1]}")

# get user with the highest average sleep quality
best_sleeper = (
    session.query(User.name, func.avg(SleepLog.quality))
    .join(User.sleep)
    .filter(SleepLog.date >= start_date)
    .group_by(User.name)
    .order_by(func.avg(SleepLog.quality).desc())
    .first()
)
# TODO: round results
print(
    f"User with the highest average sleep quality over the last month: {best_sleeper.name}, Quality: {best_sleeper[1]}"
)

# FOOD AND FOOD LOG QUERIES
# 3 most popular foods for all users
# Query the FoodLog table
query = (
    session.query(Food.name, func.count(FoodLog.food_id).label("total"))
    .join(FoodLog, Food.id == FoodLog.food_id)
    .group_by(Food.name)
    .order_by(text("total DESC"))
    .limit(3)
)

# Execute the query and fetch all results
most_popular_foods = query.all()

# Print the results
for food in most_popular_foods:
    print("\n3 most popular foods across all users")
    print(f"Food ID: {food.name}, Count: {food.total}")

# entries for user 1 in the last day
# Get the date 1 day ago
end_date = datetime.now().date()
start_date = end_date - timedelta(days=1)

# Specify the user_id
user_id = 1  # Replace with the actual user_id

# Query the FoodLog table and use the backref to Food
query = (
    session.query(FoodLog)
    .join(Food)
    .filter(
        FoodLog.user_id == user_id, FoodLog.date.between(start_date, end_date)
    )  # TODO: th user id shoudl be indexed
)

# Execute the query and fetch all results
foods_user_ate_yesterday = query.all()

# Print the results
print("\nFoods user 1 ate yesterday:")
for food_log in foods_user_ate_yesterday:
    print(f"Food Name: {food_log.food.name}, Time: {food_log.time}")


# Get the date 1 week ago
# TODO: also make start_date_7
start_date_7 = end_date - timedelta(days=7)

# Specify the user_id
user_id = 1

# Query the FoodLog table and use the backref to Food
query = (
    session.query(FoodLog)
    .join(Food)
    .filter(
        FoodLog.user_id == user_id,
        FoodLog.date.between(start_date_7, end_date),
        Food.category == 4,  # Filter by the vegetable food category
    )
)

# Execute the query and fetch all results
num_vegetables_last_week = (
    query.count()
)  # Use count() to get the number of times user 1 ate vegetables

# Print the results
print(
    f"\nNumber of times user 1 ate vegetables in the last week: {num_vegetables_last_week}"
)

# Specify the user_id and date
user_id = 1
date = datetime(2023, 11, 9)

# Query the FoodLog table and use the backref to Food
query = (
    session.query(func.sum(Food.calories).label("total_calories"))
    .join(FoodLog)
    .filter(
        FoodLog.user_id == user_id,
        FoodLog.date == date.date(),
    )
)
total_calories = query.scalar()  # Use scalar() to get the sum of calories
print(f"\nTotal calories consumed by user {user_id} on {date.date()}: {total_calories}")

# WORKOUT RECOMMENDATION QUERIES
# get a recommendation for an easy cardio workout less than 0.5 hours
# Query the WorkoutRecommendation table
query = (
    session.query(WorkoutRecommendation)
    .filter(
        WorkoutRecommendation.exercise_type == 1,
        WorkoutRecommendation.difficulty_level == 1,
        WorkoutRecommendation.duration <= 0.75,
    )
    .order_by(func.random())
)
workouts = query.all()
if workouts:
    print("\nEasy cardio workouts less than 0.75 hours:")
    for workout in workouts:
        print(f"{workout.workout_name} (Duration: {round(workout.duration, 2)} hours)")
else:
    print("\nNo matching workouts were found.")

# number of strength workouts in recommendation table
query = (
    session.query(func.count(WorkoutRecommendation.id))
    .filter(WorkoutRecommendation.exercise_type == 2)
    .scalar()
)
print(f"\nNumber of strength workouts in the recommendation table: {query}")


# # get the most frequent recommendation users used
# query = (
#     session.query(
#         WorkoutLog.recommendation_id,
#         WorkoutLog.workout_recommendations.workout_name,
#         func.count(WorkoutLog.recommendation_id),
#     )
#     .group_by(WorkoutLog.recommendation_id)
#     .order_by(desc(func.count(WorkoutLog.recommendation_id)))
#     .first()
# )
# most_frequent_rec_id, most_frequent_rec_name, frequency = query
# print(
#     f"\nThe most frequent recommendation all the users did is {most_frequent_rec_name} {frequency} times."
# )

# TODO: can make end_date_7 too
end_date = start_date_7 + timedelta(days=7)
user_id = 1
# Query the WorkoutLog table to get the number of workouts for a specific user this week
query = (
    session.query(func.count(WorkoutLog.id))
    .filter(
        WorkoutLog.user_id == user_id, WorkoutLog.date.between(start_date_7, end_date)
    )
    .scalar()
)
print(f"\nUser {user_id} worked out {query} times this week.")

workout_date = datetime.now().date() - timedelta(days=7)
# Query the WorkoutLog table to get the total calories burned by a specific user on a specific day
query = (
    session.query(func.sum(WorkoutLog.calories_burned))
    .filter(WorkoutLog.user_id == user_id, WorkoutLog.date == workout_date)
    .scalar()
)
print(f"\nUser {user_id} burned {query} calories on {workout_date}.")

# Query the WorkoutLog table to get the details of a user-created workout
workout_log = (
    session.query(WorkoutLog)
    .filter(WorkoutLog.user_id == user_id, WorkoutLog.user_workout_id.isnot(None))
    .first()
)

if workout_log is not None:
    user_workout = workout_log.user_workout
    print(
        f"\nUser {user_id} created a workout on {workout_log.date} with the following details:"
    )
    print(f"Exercise type: {user_workout.exercise_type}")
    print(f"Description: {user_workout.description}")
    print(f"Duration: {user_workout.duration} hours")
    print(f"Difficulty level: {user_workout.difficulty_level}")
    print(f"Calories burned: {workout_log.calories_burned}")
    print(f"Avg heart rate: {workout_log.heart_rate}")
else:
    print(f"User {user_id} has not created any workouts.")

# GOAL QUERIES
# Query the goals for user 1
goals = session.query(Goal).filter(Goal.user_id == 1).all()

# Check if the user has any goals
if goals:
    print("\nGoals for User 1.")
    # Print out the details of each goal
    for goal in goals:
        print(f"\nGoal ID: {goal.id}")
        print(f"Start date: {goal.start_date}")
        print(f"End date: {goal.end_date}")
        print(f"Goal type: {goal.goal_type}")
        print(f"Goal description: {goal.description}")
else:
    print("User 1 has not set any goals.")


# TODO: query how many goals the user has completed
# TODO: get the in progress goals
# TODO: get a fitness goal / check for a specific goal type to filter
# TODO: how many difficult workouts did the user complete this week? -- need to query both tables

query_end_time = time.time()
print(f"Query runtime: {query_end_time - query_start_time} seconds")
