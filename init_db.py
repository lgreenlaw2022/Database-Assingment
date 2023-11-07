from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Float,
    Time,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)
    height = Column(Float)
    email = Column(String, unique=True)
    password = Column(String)  # this will be hashed

    # understand this code better
    # This property can be used to access the parent model
    # from the child model, creating a bidirectional relationship.
    health_metrics = relationship("HealthMetric", backref="user")
    sleeps = relationship("Sleep", backref="user")
    foods = relationship("Food", backref="user")


class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate = Column(Integer)
    steps_taken = Column(Integer)  # -- could also be connected to workout table
    stand_hours = Column(Integer)
    systolic_bp = Column(Integer)
    dystolic_bp = Column(Integer)
    date = Column(Date)


class Sleep(Base):
    __tablename__ = "sleep"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    duration = Column(Float)
    quality = Column(String)  # ? notes?
    start_time = Column(Time)
    end_time = Column(Time)
    date = Column(Date)


class Food(Base):
    __tablename__ = "food"

    id = Column("FoodID", Integer, primary_key=True)
    item = Column("FoodItem", String(100), nullable=False)
    calories = Column("Calories", Integer, nullable=False)
    # what else should I store here? food type?
    """
    protein = Column('Protein', DECIMAL)
    carbohydrates = Column('Carbohydrates', DECIMAL)
        veggie_portions = Column('Veggie Portions', Integer)
    fats = Column('Fats', DECIMAL)
    """
    nutrition_logs = relationship("NutritionLog", backref="food")


class NutritionLog(Base):
    __tablename__ = "nutrition"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column("FoodID", Integer, ForeignKey("food.id"))
    date = Column(Date)
    time = Column(Time)


class WorkoutLog(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_type = Column(Integer)  # 1 = cardio, 2 = strength, 3 = flexibility
    duration = Column(Float)
    calories_burned = Column(Float)
    heart_rate = Column(Integer)  # connect this to the heart rate table?
    difficulty_level = Column(Integer)  # include in the personal log?
    date = Column(Date)
    notes = Column(String)


class WorkoutRecommendation(Base):
    __tablename__ = "workout_recommendations"
    id = Column(Integer, primary_key=True)
    workout_name = Column(String)
    description = Column(String)
    duration = Column(Float)
    calories_burned = Column(Float)
    difficulty_level = Column(Integer)  # 1 = easy, 2 = medium, 3 = hard


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Integer)  # 0 = not started, 1 = complete, 2 = in progress
