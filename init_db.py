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
    event,
    Index,
)
from sqlalchemy.orm import relationship, backref, declarative_base

engine = create_engine("sqlite:///health_database.db")


# enable foreign key support for sqlite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


Base = declarative_base()


# User table stores user log in and personal information
class User(Base):
    __tablename__ = "users"
    """
    PK choice:
    the email is immutable and unique, so it is a good candidate for a PK
    however, a string is not as efficient than an integer PK and almost all the 
    queries will require the user id. Email is also not an intuitive way to search for a user
    The surrogate id is a more efficient choice that is guaranteed to be unique
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, CheckConstraint("age>=0"))
    gender = Column(
        Integer, CheckConstraint("gender BETWEEN 1 AND 3")
    )  # gender: "Male", "Female", "Nonbinary"
    weight = Column(Float, CheckConstraint("weight>=0"))  # kg
    height = Column(Float, CheckConstraint("height>=0"))  # cm
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # create 2 way relationship between tables that use user_id as a FK
    # this increases query efficiency because I do not have to manually
    # connect the tables on the id column
    sleep_log = relationship("SleepLog", backref="user")
    food_log = relationship("FoodLog", backref="user")
    workout_log = relationship("WorkoutLog", backref="user")
    goals = relationship("Goal", backref="user")
    health_metrics = relationship("HealthMetric", backref="user")


# health metric table tracks health metrics over time for users
class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    # assume the metrics are added by a smart device, allowing for comprehensive reports
    heart_rate = Column(Integer, CheckConstraint("heart_rate>=0"))
    steps_taken = Column(Integer, CheckConstraint("steps_taken>=0"))
    stand_hours = Column(Integer, CheckConstraint("stand_hours>=0"))
    systolic_bp = Column(Integer, CheckConstraint("systolic_bp>=0"))
    diastolic_bp = Column(Integer, CheckConstraint("diastolic_bp>=0"))
    timestamp = Column(DateTime, nullable=False)

    # Create a composite index on user_id and timestamp
    Index("idx_healthmetrics_userid_timestamp", "user_id", "timestamp")


# sleep log table tracks sleep habits and quality for users
class SleepLog(Base):
    __tablename__ = "sleep_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    # TODO: make a case for this being 2NF
    duration = Column(Float, CheckConstraint("duration>=0"))
    quality = Column(
        Integer, CheckConstraint("quality BETWEEN 1 AND 5")
    )  # 1 = poor, 2 = fair, 3 = good, 4 = excellent
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)

    # Create a composite index on user_id and date
    Index("idx_sleeplog_userid_date", "user_id", "date")


# food table defines the food options available to users (new options can be added)
class Food(Base):
    __tablename__ = "food"
    # name is not primary key because it may be updated or the other entries may vary
    id = Column(Integer, primary_key=True)
    # assume drop down for entry normalization of name
    name = Column(String(100), nullable=False, unique=True)
    calories = Column(Integer, CheckConstraint("calories>=0"), nullable=False)
    category = Column(
        Integer, CheckConstraint("category BETWEEN 1 AND 5"), nullable=False
    )  # 1 = protein, 2 = carb, 3 = fat, 4 = veggie, 5 = fruit


# food log table tracks food intake over time for users by referencing the food table
class FoodLog(Base):
    __tablename__ = "food_log"
    # need the surrogate key here because otherwise the whole table would be a composite key
    # a user may eat the same food multiple times a day etc
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    food_id = Column(Integer, ForeignKey("food.id"), index=True, nullable=False)
    # want to keep these separate because a user might want a daily report with times
    # or a long term report with dates
    date = Column(Date, nullable=False)
    time = Column(Time)

    food = relationship("Food", backref="food_log")

    # Create a composite index on user_id and date
    Index("idx_foodlog_userid_date", "user_id", "date")


# workout log tracks workouts completed by user and their stats
class WorkoutLog(Base):
    """
    This is a relational table that connects the user to either a user workout or
    a recommended workout. It is a many to many relationship because a user repeat
    a workout many times and a workout can be done by many users. Both options are
    included here because there are metrics applicable to both workouts than cannot be
    predicted in the workout definition (calories burned, heart rate).
    """

    __tablename__ = "workout_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_workout_id = Column(Integer, ForeignKey("user_workout.id"), index=True)
    recommendation_id = Column(
        Integer, ForeignKey("workout_recommendation.id"), index=True
    )
    calories_burned = Column(Integer, CheckConstraint("calories_burned > 0"))
    heart_rate = Column(Integer, CheckConstraint("heart_rate > 0"))
    date = Column(Date, nullable=False)

    __table_args__ = (
        # ensure that only one workout is listed: a user workout or a recommended one
        CheckConstraint(
            "(user_workout_id IS NULL AND recommendation_id IS NOT NULL) OR "
            "(user_workout_id IS NOT NULL AND recommendation_id IS NULL)",
            name="chk_workout_recommendation_exclusive",
        ),
    )
    workout_recommendation = relationship(
        "WorkoutRecommendation", backref="workout_log"
    )
    user_workout = relationship("UserWorkout", backref="workout_log")

    Index("idx_workoutlog_userid_date", "user_id", "date")


# user workout table holds workouts the USER defines
# the assumption is that through the app or website, when a user logs a workout they made,
# it is immediately added to the workout log table and connected with the user_id
class UserWorkout(Base):
    __tablename__ = "user_workout"
    id = Column(Integer, primary_key=True)
    exercise_type = Column(
        Integer,
        CheckConstraint("exercise_type IN (1, 2, 3)"),
        nullable=False,
    )  # 1 = cardio, 2 = strength, 3 = flexibility
    description = Column(String, nullable=False)
    duration = Column(
        Float, CheckConstraint("duration BETWEEN 0 AND 3"), nullable=False
    )  # hours
    difficulty_level = Column(
        Integer, CheckConstraint("difficulty_level IN (1, 2, 3)"), nullable=False
    )  # 1 = easy, 2 = medium, 3 = hard


# workout recommendation table holds generalized lists of data for users to choose from
# characteristics are stored for improved recommendation filters
class WorkoutRecommendation(Base):
    __tablename__ = "workout_recommendation"

    id = Column(Integer, primary_key=True)
    # could have the same name for multiple difficulty levels or durations so this cannot be the PK
    workout_name = Column(String(100), nullable=False)
    description = Column(String(255))
    exercise_type = Column(
        Integer,
        CheckConstraint("exercise_type IN (1, 2, 3)"),
        nullable=False,
    )  # 1 = cardio, 2 = strength, 3 = flexibility
    duration = Column(
        Float, CheckConstraint("duration BETWEEN 0 AND 3"), nullable=False
    )  # hours
    difficulty_level = Column(
        Integer, CheckConstraint("difficulty_level IN (1, 2, 3)"), nullable=False
    )  # 1 = easy, 2 = medium, 3 = hard


# goal table tracks details of user goals and their status
class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    description = Column(String(255), nullable=False)
    # can get goal status based on start and end date
    # user can change dates if needed
    start_date = Column(Date)
    end_date = Column(Date)
    # goal type helps with filtering and reporting
    goal_type = Column(
        Integer, CheckConstraint("goal_type IN (1,2,3)")
    )  # 1 = sleep, 2 = nutrition, 3 = workout

    __table_args__ = (
        # check goal starts before the end date
        CheckConstraint(start_date < end_date, name="check_start_date_before_end_date"),
    )


Base.metadata.create_all(engine)
