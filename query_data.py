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
from datetime import datetime, timedelta, date
import time

# track run time for query processing
query_start_timestamp = time.time()
# # Get the date 30 days ago
start_date_30 = datetime.now() - timedelta(days=30)
start_date_7 = datetime.now() - timedelta(days=7)

### USER TABLE QUERIES ###
print("First 5 users:")
all_users = session.query(User).limit(5).all()
for user in all_users:
    print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")

print("\nTotal User Count:")
user_count = session.query(func.count(User.id)).scalar()
print(user_count)

### HEALTH_METRIC TABLE QUERIES ###
# Get the user with id 1

user_id = 1
user1 = session.query(User).filter(User.id == user_id).first()

while not user1:
    user_id += 1
    user1 = session.query(User).filter(User.id == user_id).first()

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
        HealthMetric.timestamp >= start_date_30,
    )
    .first()
)
print(f"\nAverage health metrics for {user1.name} over the last 30 days:")
print(
    f"Heart Rate: {avg_metrics[0]}, Steps Taken: {avg_metrics[1]}, Stand Hours: {avg_metrics[2]}"
)
print(f"Systolic BP: {avg_metrics[3]}, Diastolic BP: {avg_metrics[4]}")


# Get average steps taken over the last 7 days
avg_steps = (
    session.query(
        func.avg(HealthMetric.steps_taken),
    )
    .filter(
        HealthMetric.user_id == user1.id,
        HealthMetric.timestamp >= start_date_7,
    )
    .scalar()
)
print(f"\nAverage steps per day for {user1.name} over the last 7 days: {avg_steps}")

### SLEEP TABLE QUERIES ###
# get average sleep quality and duration for user 1 over the last 30 days
# Get today's date
end_date = datetime.now()
avg_sleep = (
    session.query(
        func.avg(SleepLog.duration),
        func.avg(SleepLog.quality),
    )
    .filter(
        SleepLog.user_id == user1.id,
        SleepLog.date.between(start_date_30, end_date),
    )
    .first()
)
print(f"\nAverage sleep duration and quality for {user1.name} over the last 30 days:")
print(f"Duration: {avg_sleep[0]}, Quality: {avg_sleep[1]}")


# get user with the highest average sleep quality in the last month
best_sleeper = (
    session.query(User.name, func.avg(SleepLog.quality))
    .join(User.sleep_log)  # using backref
    .filter(SleepLog.date >= start_date_30)
    .group_by(User.name)
    .order_by(func.avg(SleepLog.quality).desc())
    .first()
)
print(f"\nUser with the highest average sleep quality over the last month:")
print(f"{best_sleeper.name}, Quality: {best_sleeper[1]}")

### FOOD AND FOOD LOG QUERIES ###
# 3 most popular foods for all users
query = (
    session.query(Food.name, func.count(FoodLog.food_id).label("total"))
    .join(FoodLog)  # did not have to do a JOIN because of backref
    .group_by(Food.name)
    .order_by(text("total DESC"))
    .limit(3)
)
most_popular_foods = query.all()
print("\n3 most popular foods across all users")
for food in most_popular_foods:
    print(f"Food ID: {food.name}, Count: {food.total}")

# Food log entries for user 1 yesterday
# Get the date 1 day ago
query_date = datetime.now().date() - timedelta(days=1)
foods_user_ate_yesterday = (
    session.query(FoodLog)
    .join(Food)  # backref removes the need for explicit join condition
    .filter(FoodLog.user_id == user1.id, FoodLog.date == query_date)
).all()

print("\nFoods user 1 ate yesterday:")
for food_log in foods_user_ate_yesterday:
    print(f"Food Name: {food_log.food.name}, Time: {food_log.time}")


# Query the FoodLog table and use the backref to Food
query = (
    session.query(FoodLog)
    .join(Food)  # using backrf
    .filter(
        FoodLog.user_id == user1.id,
        FoodLog.date.between(start_date_7, end_date),
        Food.category == 4,  # Filter by the vegetable food category
    )
)
num_vegetables_last_week = (
    query.count()
)  # Use count() to get the number of times user 1 ate vegetables
print(
    f"\nNumber of times user 1 ate vegetables in the last week: {num_vegetables_last_week}"
)

# total calories eaten by user1 that day
query_date = datetime(2023, 11, 8)
query = (
    session.query(func.sum(Food.calories))
    .join(FoodLog)
    .filter(
        FoodLog.user_id == user1.id,
        FoodLog.date == query_date.date(),
    )
)
total_calories = query.scalar()
print(
    f"\nTotal calories consumed by user {user1.id} on {query_date.date()}: {total_calories}"
)


### WORKOUT RECOMMENDATION QUERIES ###
# get a recommendation for an easy cardio workout less than 0.75 hours
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

### Workout Log Queries ###
# get the most frequent recommendation users used
query = (
    session.query(
        WorkoutLog.recommendation_id,
        func.count(WorkoutLog.recommendation_id),
    )
    .group_by(WorkoutLog.recommendation_id)
    .order_by(desc(func.count(WorkoutLog.recommendation_id)))
    .first()
)
most_frequent_rec_id, frequency = query
print(
    f"\nThe most frequent recommendation all the users did is workout{most_frequent_rec_id}: {frequency} times."
)

# Query the WorkoutLog table to get the number of workouts for a specific user this week
end_date = start_date_7 + timedelta(days=7)
num_workouts = (
    session.query(func.count(WorkoutLog.id))
    .filter(
        WorkoutLog.user_id == user1.id,
        WorkoutLog.date.between(start_date_7, end_date),
    )
    .scalar()
)
print(f"\nUser {user1.name} worked out {num_workouts} times this week.")

# Query the WorkoutLog table to get the total calories burned by a specific user on a specific day
workout_date = datetime.now().date() - timedelta(days=7)
query = (
    session.query(func.sum(WorkoutLog.calories_burned))
    .filter(WorkoutLog.user_id == user1.id, WorkoutLog.date == workout_date)
    .scalar()
)
print(f"\nUser {user1.name} burned {query} calories on {workout_date}.")

# Query the WorkoutLog table to get the details of a user-created workout
workout_log = (
    session.query(WorkoutLog)
    .filter(WorkoutLog.user_id == user1.id, WorkoutLog.user_workout_id.isnot(None))
    .first()
)
if workout_log is not None:
    user_workout = workout_log.user_workout  # uses backref
    print(
        f"\nUser {user1.name} created a workout on {workout_log.date} with the following details:"
    )
    print(f"Exercise type: {user_workout.exercise_type}")
    print(f"Description: {user_workout.description}")
    print(f"Duration: {user_workout.duration} hours")
    print(f"Difficulty level: {user_workout.difficulty_level}")
    print(f"Calories burned: {workout_log.calories_burned}")
    print(f"Avg heart rate: {workout_log.heart_rate}")
else:
    print(f"User {user1.name} has not created any workouts.")


### GOAL QUERIES ###
# Query the goals for user 1
goals = user1.goals  # using backref here speeds up the query and makes it more readable
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

# get the number of completed goals for user 1
completed_goals_count = (
    session.query(func.count(Goal.id))  # Count the goals
    .filter(
        Goal.user_id == user1.id,
        Goal.end_date < date.today(),  # Filter by end date
    )
    .scalar()  # Get the count
)
print(f"\nNumber of completed goals by user {user1.id}: {completed_goals_count}")

# get the details of in progress goals for user 1

in_progress_goals = (
    session.query(Goal)  # Select the goals
    .filter(
        Goal.user_id == user1.id,
        Goal.start_date <= date.today(),  # Filter by start date
        Goal.end_date >= date.today(),  # Filter by end date
    )
    .all()  # Get all matching records
)

print(f"\nIn-progress goals by user {user1.id}:")
for goal in in_progress_goals:
    print(
        f"Goal ID: {goal.id}, Start Date: {goal.start_date}, End Date: {goal.end_date}, Type: {goal.goal_type}"
    )


# get in progress fitness goals for user 1
goal_type = 3  # fitness goal
fitness_goals = (
    session.query(Goal)  # Select the goals
    .filter(
        Goal.user_id == user1.id,
        Goal.goal_type == goal_type,  # Filter by type
        Goal.end_date >= date.today(),  # in progress goals
    )
    .all()  # Get all matching records
)
if fitness_goals:
    print(f"\nIn progress fitness goals for user {user1.id}:")
    for goal in fitness_goals:
        print(
            f"Goal ID: {goal.id}, Start Date: {goal.start_date}, End Date: {goal.end_date}"
        )
else:
    print("\nno in progress fitness goals for user")


# generate monthly health report for user 1
# Get the current date and the date 30 days ago
current_date = datetime.now().date()
start_date_30 = current_date - timedelta(days=30)

# Get average health metrics over the last 30 days
avg_metrics = (
    session.query(
        func.round(func.avg(HealthMetric.heart_rate), 2).label(
            "avg_resting_heart_rate"
        ),
        func.round(func.avg(HealthMetric.steps_taken), 2).label("avg_steps_taken"),
        func.round(func.avg(HealthMetric.stand_hours), 2).label("avg_stand_hours"),
        func.round(func.avg(HealthMetric.systolic_bp), 2).label("avg_systolic_bp"),
        func.round(func.avg(HealthMetric.diastolic_bp), 2).label("avg_diastolic_bp"),
    )
    .filter(
        HealthMetric.user_id == user1.id,
        HealthMetric.timestamp >= start_date_30,
    )
    .first()
)
# Get average sleep duration and quality over the last 30 days
avg_sleep = (
    session.query(
        func.round(func.avg(SleepLog.duration), 2).label("avg_sleep_duration"),
        func.round(func.avg(SleepLog.quality), 2).label("avg_sleep_quality"),
    )
    .filter(
        SleepLog.user_id == user1.id,
        SleepLog.date >= start_date_30,
    )
    .first()
)
# Get average number of calories per day over the last 30 days
# Get sum of calories per day over the last 30 days
calories_per_day = (
    session.query(FoodLog.date, func.sum(Food.calories).label("calories"))
    .join(FoodLog, FoodLog.food_id == Food.id)
    .filter(
        FoodLog.user_id == user1.id,
        FoodLog.date >= start_date_30,
    )
    .group_by(FoodLog.date)
    .subquery()
)
# Get average calories per day
avg_calories = (
    session.query(
        func.round(func.avg(calories_per_day.c.calories), 2).label("avg_calories")
    )
    .select_from(calories_per_day)
    .scalar()
)
# Get number of goals completed this month
goals_completed = (
    session.query(func.count(Goal.id))
    .filter(
        Goal.user_id == user1.id,
        Goal.end_date.between(start_date_30, current_date),
    )
    .scalar()
)
# Get number of workouts completed over the last 30 days
workouts_completed = (
    session.query(func.count(WorkoutLog.id))
    .filter(
        WorkoutLog.user_id == user1.id,
        WorkoutLog.date >= start_date_30,
    )
    .scalar()
)
# Print the health report
print(f"\n30-Day Health Report for {user1.name}:")
print(f"Average Heart Rate: {avg_metrics.avg_resting_heart_rate}")
print(f"Average Steps Taken: {avg_metrics.avg_steps_taken}")
print(f"Average Stand Hours: {avg_metrics.avg_stand_hours}")
print(f"Average Systolic BP: {avg_metrics.avg_systolic_bp}")
print(f"Average Diastolic BP: {avg_metrics.avg_diastolic_bp}")
print(f"Average Sleep Duration: {avg_sleep.avg_sleep_duration}")
print(f"Average Sleep Quality: {avg_sleep.avg_sleep_quality}")
print(f"Average Calories per Day: {avg_calories}")
print(f"Goals Completed This Month: {goals_completed}")
print(f"Workouts Completed: {workouts_completed}")


query_end_time = time.time()
print(f"\nTOTAL query runtime: {query_end_time - query_start_timestamp} seconds")
