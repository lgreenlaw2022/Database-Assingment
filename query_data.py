from init_db import User
from sqlalchemy import func
from db_session import session
from faker import Faker

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
