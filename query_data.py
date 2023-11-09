from init_db import User, HealthMetric
from sqlalchemy import func
from db_session import session
from faker import Faker
import random
from datetime import datetime, timedelta

# initialize Faker for transaction demonstrations
fake = Faker()

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
health_metric = HealthMetric(
    user_id=libby.id,
    heart_rate=random.randint(40, 130),
    steps_taken=random.randint(0, 20000),
    stand_hours=random.randint(0, 20),
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
