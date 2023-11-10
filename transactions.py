from init_db import User, HealthMetric, Sleep
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
