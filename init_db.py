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
    # NOTE: this is the only value that is maybeee immutable but I don't think it is
    # an intuitive PK value, and def not a composite key value
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # this will be hashed

    # identify 1:many relationships with user as FK
    # NOTE: OPTIMIZATION: you can get all goals of a user by accessing user.goals
    # and you can get the user of a goal by accessing goal.user
    # SQLAlchemy can use a JOIN in the query to avoid an extra round trip to the database.
    health_metrics = relationship("HealthMetric", backref="user")
    sleep = relationship("Sleep", backref="user")
    # foods = relationship("Food", backref="user") TODO: update if I don't need
    food_log = relationship("FoodLog", backref="user")
    # workout_log = relationship("WorkoutLog", backref="user")
    # user_workout = relationship("UserWorkout", backref="user")
    # goals = relationship("Goal", backref="user")


class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id = Column(Integer, primary_key=True)
    # TODO: maybe I should make it so all of these are required, assuming a smart device
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    heart_rate = Column(Integer, CheckConstraint("heart_rate>=0"))
    steps_taken = Column(Integer, CheckConstraint("steps_taken>=0"))
    stand_hours = Column(Integer, CheckConstraint("stand_hours>=0"))
    systolic_bp = Column(Integer, CheckConstraint("systolic_bp>=0"))
    diastolic_bp = Column(Integer, CheckConstraint("diastolic_bp>=0"))
    timestamp = Column(DateTime, nullable=False)


class Sleep(Base):  # TODO: change this to sleep log?
    __tablename__ = "sleep"
    id = Column(Integer, primary_key=True)
    # TODO: do I need this index if I can do the backref relationship?
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    # TODO: can I make a case for using this? because I think it is a highly requested data
    # TODO: change insertions to correctly calculate insertions
    # TODO: need to validate this somehow?
    duration = Column(Float, CheckConstraint("duration>=0"), nullable=False)
    # TODO: still decide about numbering
    quality = Column(
        Integer, CheckConstraint("quality BETWEEN 1 AND 5")
    )  # 1 = poor, 2 = fair, 3 = good, 4 = excellent
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)


class Food(Base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True)  # TODO: need another id for the food?
    name = Column(String(100), nullable=False, unique=True)
    # assume drop down for entry normalization
    calories = Column(Integer, CheckConstraint("calories>=0"), nullable=False)
    category = Column(
        Integer, CheckConstraint("category BETWEEN 1 AND 5"), nullable=False
    )  # 1 = protein, 2 = carb, 3 = fat, 4 = veggie, 5 = fruit

    food_logs = relationship("FoodLog", backref="food")


class FoodLog(Base):
    __tablename__ = "food_log"
    # need the key here because otherwise the whole table would be a composite key
    # a user may eat the same food multiple times a day etc
    id = Column(Integer, primary_key=True)
    # not sure if I need this index if I have the back  ref
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    food_id = Column(Integer, ForeignKey("food.id"), index=True, nullable=False)
    # want to keep these separate because a user might want a daily report with times
    # or a long term report with dates
    date = Column(Date, nullable=False)
    time = Column(Time)


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


# workout table -- store workout stats
class UserWorkout(Base):
    __tablename__ = "user_workout"
    # TODO: make sure that the user workouts will be added to the log table immediately
    id = Column(Integer, primary_key=True)
    exercise_type = Column(
        Integer,
        CheckConstraint("exercise_type IN (1, 2, 3)"),
        nullable=False,
    )  # 1 = cardio, 2 = strength, 3 = flexibility
    description = Column(String, nullable=False)
    duration = Column(
        Float, CheckConstraint("duration BETWEEN 0 AND 3"), nullable=False
    )
    difficulty_level = Column(
        Integer, CheckConstraint("difficulty_level IN (1, 2, 3)"), nullable=False
    )  # include in the personal log?

    # workout_log = relationship(
    #     "WorkoutLog", backref="user_workout"
    # )


class WorkoutRecommendation(Base):
    __tablename__ = "workout_recommendations"

    id = Column(Integer, primary_key=True)
    # could have the same name for multiple difficulty levels or durations so this cannot be the PK
    workout_name = Column(
        String(100), nullable=False
    )  # TODO: check if I need to delete this
    description = Column(String)
    exercise_type = Column(
        Integer,
        CheckConstraint("exercise_type IN (1, 2, 3)"),
        nullable=False,
    )  # 1 = cardio, 2 = strength, 3 = flexibility
    duration = Column(
        Float, CheckConstraint("duration BETWEEN 0 AND 3"), nullable=False
    )
    difficulty_level = Column(
        Integer, CheckConstraint("difficulty_level IN (1, 2, 3)"), nullable=False
    )  # 1 = easy, 2 = medium, 3 = hard

    # workout_log = relationship("WorkoutLog", backref="workout_recommendation")


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
