from init_db import User, HealthMetric, Sleep, Food, FoodLog
from sqlalchemy import func, text
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
# USER TABLE QUERIES
print("First 5 users:")
all_users = session.query(User).limit(5).all()
for user in all_users:
    print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")

print("\nTotal User Count:")
user_count = session.query(func.count(User.id)).scalar()
print(user_count)

# Inserting a new user
# TODO: maybe make the indexes for these queries because its hard to get a user
# new_user = User(
#     name="Libby Greenlaw",
#     age=18,
#     gender="Female",
#     weight=130,
#     height=170,
#     email="libbygreenlaw18@example.com",
#     password=fake.password(),
# )
# session.add(new_user)
# session.commit()
# print(
#     f"\nadded user: Name: {new_user.name}, Age: {new_user.age}, Email: {new_user.email}"
# )

# print("New User Count after insertion:")
# user_count = session.query(func.count(User.id)).scalar()
# print(user_count)

# libby = new_user


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

# Add health metrics for libby
# TODO: hardcode some so that we can tell it is correct
# health_metric = HealthMetric(
#     user_id=libby.id,
#     heart_rate=75,
#     steps_taken=7000,
#     stand_hours=10,
#     systolic_bp=random.randint(90, 130),
#     diastolic_bp=random.randint(20, 90),
#     timestamp=datetime.now(),
# )
# session.add(health_metric)
# session.commit()

# Get the last health metric for libby
# last_metric = (
#     session.query(HealthMetric)
#     .filter(HealthMetric.user_id == libby.id)
#     .order_by(HealthMetric.timestamp.desc())
#     .first()
# )

# if last_metric:
#     print(f"\nLast health metric for {libby.name}:")
#     print(
#         f"Heart Rate: {last_metric.heart_rate}, Steps Taken: {last_metric.steps_taken}, Stand Hours: {last_metric.stand_hours}, Systolic BP: {last_metric.systolic_bp}, Diastolic BP: {last_metric.diastolic_bp}"
#     )
# else:
#     print("No health metrics found for this user.")


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
            func.avg(Sleep.duration),
            func.avg(Sleep.quality),
        )
        .filter(
            Sleep.user == user1,
            Sleep.date.between(start_date, end_date),
        )
        .first()
    )

    print(
        f"\nAverage sleep duration and quality for {user1.name} over the last 30 days:"
    )
    print(f"Duration: {avg_sleep[0]}, Quality: {avg_sleep[1]}")

# get user with the highest average sleep quality
best_sleeper = (
    session.query(User.name, func.avg(Sleep.quality))
    .join(User.sleep)
    .filter(Sleep.date >= start_date)
    .group_by(User.name)
    .order_by(func.avg(Sleep.quality).desc())
    .first()
)
# TODO: round results
print(
    f"User with the highest average sleep quality over the last month: {best_sleeper.name}, Quality: {best_sleeper[1]}"
)

# add a sleep record for libby
# sleep = Sleep(
#     user_id=libby.id,
#     duration=8,
#     quality=4,
#     start_time=datetime.now().time(),
#     end_time=datetime.now().time(),
#     date=datetime.now().date(),
# )
# session.add(sleep)
# session.commit()

# # Get the last sleep record for libby
# last_sleep = (
#     session.query(Sleep)
#     .filter(Sleep.user_id == libby.id)  # TODO: necessary?
#     .order_by(Sleep.date.desc())
#     .first()
# )

# if last_sleep:
#     print(f"\nLast sleep record for {libby.name}:")
#     print(
#         f"Date: {last_sleep.date} \nDuration: {last_sleep.duration}, Quality: {last_sleep.quality}, Start Time: {last_sleep.start_time}, End Time: {last_sleep.end_time}"
#     )


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
start_date = end_date - timedelta(days=7)

# Specify the user_id
user_id = 1

# Query the FoodLog table and use the backref to Food
query = (
    session.query(FoodLog)
    .join(Food)
    .filter(
        FoodLog.user_id == user_id,
        FoodLog.date.between(start_date, end_date),
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

# Execute the query and fetch the result
total_calories = query.scalar()  # Use scalar() to get the sum of calories

# Print the result
print(f"\nTotal calories consumed by user {user_id} on {date.date()}: {total_calories}")
