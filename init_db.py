from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Float,
    Time,
    CheckConstraint,
    DateTime,
)
from sqlalchemy.orm import relationship, backref, declarative_base

engine = create_engine("sqlite:///health_database.db")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    # there can be repeating names eg John Smith, so there is no way
    # to get these values without the id
    age = Column(Integer, CheckConstraint("age>=0"))
    # TODO: can't decide if this should be preset with numbers
    gender = Column(String(10))
    weight = Column(Float, CheckConstraint("weight>=0"))
    height = Column(Float, CheckConstraint("height>=0"))
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # this will be hashed

    # identify 1:many relationships with user as FK
    # NOTE: OPTIMIZATION: you can get all goals of a user by accessing user.goals
    # and you can get the user of a goal by accessing goal.user
    # SQLAlchemy can use a JOIN in the query to avoid an extra round trip to the database.
    health_metrics = relationship("HealthMetric", backref="user")
    # sleep = relationship("Sleep", backref="user")
    # foods = relationship("Food", backref="user")
    # workout_log = relationship("WorkoutLog", backref="user")
    # user_workout = relationship("UserWorkout", backref="user")
    # nutrition_log = relationship("NutritionLog", backref="user")
    # goals = relationship("Goal", backref="user")


class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    heart_rate = Column(Integer, CheckConstraint("heart_rate>=0"))
    steps_taken = Column(Integer, CheckConstraint("steps_taken>=0"))
    stand_hours = Column(Integer, CheckConstraint("stand_hours>=0"))
    systolic_bp = Column(Integer, CheckConstraint("systolic_bp>=0"))
    diastolic_bp = Column(Integer, CheckConstraint("diastolic_bp>=0"))
    timestamp = Column(DateTime, nullable=False)


# class Sleep(Base):
#     __tablename__ = "sleep"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     duration = Column(Float)
#     quality = Column(Integer)  # 1 = poor, 2 = fair, 3 = good, 4 = excellent
#     start_time = Column(Time)
#     end_time = Column(Time)
#     date = Column(Date)


# class Food(Base):
#     __tablename__ = "food"

#     id = Column(
#         "FoodID", Integer, primary_key=True
#     )  # TODO: need another id for the food?
#     user_id = Column(Integer, ForeignKey("users.id"))
#     name = Column("FoodItem", String(100), nullable=False)
#     # assume drop down for entry normalization
#     calories = Column("Calories", Integer, nullable=False)
#     category = Column(
#         "Category", Integer, nullable=False
#     )  # 1 = protein 2 = carb 3 = fat 4 = veggie 5 = fruit

#     nutrition_logs = relationship("NutritionLog", backref="food")


# class NutritionLog(Base):
#     __tablename__ = "nutrition"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     food_id = Column("FoodID", Integer, ForeignKey("food.id"))
#     date = Column(Date)
#     time = Column(Time)


# class WorkoutLog(Base):
#     __tablename__ = "workouts"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     user_workout_id = Column(Integer, ForeignKey("user-workout.id"))
#     recommendation_id = Column(Integer, ForeignKey("recommendation.id"))
#     calories_burned = Column(Float)
#     heart_rate = Column(Integer)
#     date = Column(Date)

#     __table_args__ = (
#         CheckConstraint(
#             "(workout_id IS NULL AND recommendation_id IS NOT NULL) OR "
#             "(workout_id IS NOT NULL AND recommendation_id IS NULL)",
#             name="chk_workout_recommendation_exclusive",
#         ),
#     )


# # TODO: still can't decide if the user workouts and workout recommendations are too similar
# ## workout table -- store workout stats
# class UserWorkout(Base):
#     __tablename__ = "workout"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     exercise_type = Column(Integer)  # 1 = cardio, 2 = strength, 3 = flexibility
#     description = Column(String)
#     duration = Column(Float)
#     difficulty_level = Column(Integer)  # include in the personal log?

#     workout_log = relationship(
#         "WorkoutLog", backref="user_workout"
#     )  # TODO: is this right?

# TODO: this is many to many relationship where multiple users can do th recommended workout, look into a relational table hmmm is it already though?
# class WorkoutRecommendation(Base):
#     __tablename__ = "workout_recommendations"
#     id = Column(Integer, primary_key=True)
#     exercise_type = Column(Integer)  # 1 = cardio, 2 = strength, 3 = flexibility
#     workout_name = Column(String)  # TODO: check if I need to delete this
#     description = Column(String)
#     duration = Column(Float)
#     difficulty_level = Column(Integer)  # 1 = easy, 2 = medium, 3 = hard


# class Goal(Base):
#     __tablename__ = "goals"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     description = Column(String)
#     start_date = Column(Date)
#     end_date = Column(Date)
#     # can get goal status based on start and end date
#     goal_type = Column(
#         Integer
#     )  # 1 = sleep, 2 = nutrition, 3 = workout ---> indicates which table to look into
#     # query by start and end date, and user id


Base.metadata.create_all(engine)
