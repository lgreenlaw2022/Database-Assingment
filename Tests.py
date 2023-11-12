import unittest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, date
from init_db import (
    Base,
    Goal,
    User,
    HealthMetric,
    SleepLog,
    Food,
    FoodLog,
    WorkoutRecommendation,
    UserWorkout,
    WorkoutLog,
)  # import the models to test

# These test classes verify the functionality of the models
# Tested: CRUD operations, CheckConstraints, Foregin key constraints, and basic queries


class BaseTestCase(unittest.TestCase):
    # base test case class that sets up the test database
    def setUp(self):
        # Set up the test database
        self.engine = create_engine(
            "sqlite:///:memory:"
        )  # Use an in-memory SQLite database for testing

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)  # Create the tables in the database

    def tearDown(self):
        # Clean up the test database
        Base.metadata.drop_all(self.engine)
        self.session.close()


class TestUser(BaseTestCase):
    # test User model
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.session.add(self.user)
        self.session.commit()

    def test_user_creation(self):
        # Test that the user was created
        self.assertIsNotNone(self.user.id)

    def test_user_update(self):
        # Test that you can update the user
        self.user.name = "Updated User"
        self.session.commit()
        self.assertEqual(self.user.name, "Updated User")

    def test_user_delete(self):
        # Test that you can delete the user
        self.session.delete(self.user)
        self.session.commit()
        self.assertIsNone(self.session.get(User, self.user.id))

    def test_user_name_not_null_constraint(self):
        # Test that the name not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.name = None
            self.session.commit()

    def test_user_age_constraint(self):
        # Test that the age constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.age = -1
            self.session.commit()

    def test_user_weight_constraint(self):
        # Test that the weight constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.weight = -1
            self.session.commit()

    def test_user_height_constraint(self):
        # Test that the height constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.height = -1
            self.session.commit()

    def test_email_not_null_constraint(self):
        # Test that the email not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.email = None
            self.session.commit()

    def test_password_not_null_constraint(self):
        # Test that the password not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user.password = None
            self.session.commit()

    # test possible queries
    def test_get_user_by_id(self):
        user = self.session.get(User, self.user.id)
        self.assertEqual(user.id, self.user.id)

    def test_get_user_by_email(self):
        user = self.session.query(User).filter(User.email == self.user.email).first()
        self.assertEqual(user.email, self.user.email)

    def test_get_all_users(self):
        users = self.session.query(User).all()
        self.assertEqual(len(users), 1)

    def test_get_users_by_condition(self):
        users = self.session.query(User).filter(User.age > 25).all()
        self.assertEqual(len(users), 1)


class TestHealthMetric(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.session.add(self.user)
        self.session.commit()

        # Create a health metric for the user
        self.metric = HealthMetric(
            user_id=self.user.id,
            heart_rate=70,
            steps_taken=10000,
            stand_hours=12,
            systolic_bp=120,
            diastolic_bp=80,
            timestamp=datetime.now(),
        )
        self.session.add(self.metric)
        self.session.commit()

    def test_health_metric_creation(self):
        # Test that the health metric was created
        self.assertIsNotNone(self.metric.id)

    def test_health_metric_update(self):
        # Test that you can update the health metric
        self.metric.heart_rate = 80
        self.session.commit()
        self.assertEqual(self.metric.heart_rate, 80)

    def test_health_metric_delete(self):
        # Test that you can delete the health metric
        self.session.delete(self.metric)
        self.session.commit()
        self.assertIsNone(self.session.get(HealthMetric, self.metric.id))

    def test_heart_rate_constraint(self):
        # Test that the heart_rate constraint is enforced
        with self.assertRaises(IntegrityError):
            self.metric.heart_rate = -1
            self.session.commit()

    def test_steps_taken_constraint(self):
        # Test that the steps_taken constraint is enforced
        with self.assertRaises(IntegrityError):
            self.metric.steps_taken = -1
            self.session.commit()

    def test_stand_hours_constraint(self):
        # Test that the stand_hours constraint is enforced
        with self.assertRaises(IntegrityError):
            self.metric.stand_hours = -1
            self.session.commit()

    def test_systolic_bp_constraint(self):
        # Test that the systolic_bp constraint is enforced
        with self.assertRaises(IntegrityError):
            self.metric.systolic_bp = -1
            self.session.commit()

    def test_diastolic_bp_constraint(self):
        # Test that the diastolic_bp constraint is enforced
        with self.assertRaises(IntegrityError):
            self.metric.diastolic_bp = -1
            self.session.commit()

    def test_user_id_foreign_key_constraint(self):
        # Test that the user_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_metric = HealthMetric(
                user_id=9999,
                heart_rate=70,
                steps_taken=10000,
                stand_hours=12,
                systolic_bp=120,
                diastolic_bp=80,
                timestamp=datetime.now(),
            )
            self.session.add(invalid_metric)
            self.session.commit()

    # test possible queries
    def test_get_health_metric_by_id(self):
        metric = self.session.get(HealthMetric, self.metric.id)
        self.assertEqual(metric.id, self.metric.id)

    def test_get_all_health_metrics_for_user(self):
        metrics = (
            self.session.query(HealthMetric)
            .filter(HealthMetric.user_id == self.user.id)
            .all()
        )
        self.assertEqual(len(metrics), 1)

    def test_get_health_metrics_by_condition(self):
        metrics = (
            self.session.query(HealthMetric)
            .filter(HealthMetric.steps_taken > 5000)
            .all()
        )
        self.assertEqual(len(metrics), 1)


class TestSleep(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.session.add(self.user)
        self.session.commit()

        # Create a sleep record for the user
        start_time = datetime.now()
        hours = 8
        duration = timedelta(hours=hours)
        self.sleep = SleepLog(
            user_id=self.user.id,
            duration=hours,
            quality=3,
            start_time=start_time.time(),
            end_time=(start_time + duration).time(),
            date=start_time.date(),
        )
        self.session.add(self.sleep)
        self.session.commit()

    def test_sleep_creation(self):
        # Test that the sleep record was created
        self.assertIsNotNone(self.sleep.id)

    def test_sleep_update(self):
        # Test that you can update the sleep record
        self.sleep.duration = 9
        self.session.commit()
        self.assertEqual(self.sleep.duration, 9)

    def test_sleep_delete(self):
        # Test that you can delete the sleep record
        self.session.delete(self.sleep)
        self.session.commit()
        self.assertIsNone(self.session.get(SleepLog, self.sleep.id))

    def test_sleep_duration_constraint(self):
        # Test that the sleep_duration constraint is enforced
        with self.assertRaises(IntegrityError):
            self.sleep.duration = -1
            self.session.commit()

    def test_sleep_quality_constraint(self):
        # Test that the sleep_quality constraint is enforced
        with self.assertRaises(IntegrityError):
            self.sleep.quality = 0
            self.session.commit()

    def test_user_id_foreign_key_constraint(self):
        # Test that the user_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            start_time = datetime.now()
            hours = 8
            duration = timedelta(hours=hours)
            invalid_sleep = SleepLog(
                user_id=9999,
                duration=hours,
                quality=3,
                start_time=start_time.time(),
                end_time=(start_time + duration).time(),
                date=start_time.date(),
            )
            self.session.add(invalid_sleep)
            self.session.commit()

    def test_start_time_not_null_constraint(self):
        # Test that the start_time not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.sleep.start_time = None
            self.session.commit()

    def test_end_time_not_null_constraint(self):
        # Test that the end_time not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.sleep.end_time = None
            self.session.commit()

    def test_date_not_null_constraint(self):
        # Test that the date not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.sleep.date = None
            self.session.commit()

    def test_get_sleep_log_by_id(self):
        sleep_log = self.session.get(SleepLog, self.sleep.id)
        self.assertEqual(sleep_log.id, self.sleep.id)

    def test_get_all_sleep_logs_for_user(self):
        sleep_logs = (
            self.session.query(SleepLog).filter(SleepLog.user_id == self.user.id).all()
        )
        self.assertEqual(len(sleep_logs), 1)

    def test_get_sleep_logs_by_condition(self):
        sleep_logs = self.session.query(SleepLog).filter(SleepLog.duration > 7).all()
        self.assertEqual(len(sleep_logs), 1)


class TestFood(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a food item
        self.food = Food(name="Test Food", calories=200, category=1)
        self.session.add(self.food)
        self.session.commit()

    def test_food_creation(self):
        # Test that the food item was created
        self.assertIsNotNone(self.food.id)

    def test_food_update(self):
        # Test that you can update the food item
        self.food.name = "Updated Food"
        self.session.commit()
        self.assertEqual(self.food.name, "Updated Food")

    def test_food_delete(self):
        # Test that you can delete the food item
        self.session.delete(self.food)
        self.session.commit()
        self.assertIsNone(self.session.get(Food, self.food.id))

    def test_food_name_unique_constraint(self):
        # Test that the name unique constraint is enforced
        with self.assertRaises(IntegrityError):
            duplicate_food = Food(name="Test Food", calories=300, category=2)
            self.session.add(duplicate_food)
            self.session.commit()

    def test_calories_constraint(self):
        # Test that the calories constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food.calories = -1
            self.session.commit()

    def test_category_constraint(self):
        # Test that the category constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food.category = 6
            self.session.commit()

    def test_name_not_null_constraint(self):
        # Test that the name not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food.name = None
            self.session.commit()

    def test_calories_not_null_constraint(self):
        # Test that the calories not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food.calories = None
            self.session.commit()

    def test_category_not_null_constraint(self):
        # Test that the category not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food.category = None
            self.session.commit()

    def test_get_food_by_id(self):
        food = self.session.get(Food, self.food.id)
        self.assertEqual(food.id, self.food.id)

    def test_get_food_by_name(self):
        food = self.session.query(Food).filter(Food.name == self.food.name).first()
        self.assertEqual(food.name, self.food.name)

    def test_get_all_food_in_category(self):
        foods = (
            self.session.query(Food).filter(Food.category == self.food.category).all()
        )
        self.assertEqual(len(foods), 1)

    def test_get_food_by_calories(self):
        foods = self.session.query(Food).filter(Food.calories > 150).all()
        self.assertEqual(len(foods), 1)


class TestFoodLog(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user and a food item
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.food = Food(name="Test Food", calories=200, category=1)
        self.session.add(self.user)
        self.session.add(self.food)
        self.session.commit()

        # Create a food log entry
        self.food_log = FoodLog(
            user_id=self.user.id,
            food_id=self.food.id,
            date=date.today(),
            time=datetime.now().time(),
        )
        self.session.add(self.food_log)
        self.session.commit()

    def test_food_log_creation(self):
        # Test that the food log entry was created
        self.assertIsNotNone(self.food_log.id)

    def test_food_log_update(self):
        # Test that you can update the food log entry
        self.food_log.date = date.today() - timedelta(days=1)
        self.session.commit()
        self.assertEqual(self.food_log.date, date.today() - timedelta(days=1))

    def test_food_log_delete(self):
        # Test that you can delete the food log entry
        self.session.delete(self.food_log)
        self.session.commit()
        self.assertIsNone(self.session.get(FoodLog, self.food_log.id))

    def test_user_id_foreign_key_constraint(self):
        # Test that the user_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_food_log = FoodLog(
                user_id=9999,
                food_id=self.food.id,
                date=date.today(),
                time=datetime.now().time(),
            )
            self.session.add(invalid_food_log)
            self.session.commit()

    def test_food_id_foreign_key_constraint(self):
        # Test that the food_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_food_log = FoodLog(
                user_id=self.user.id,
                food_id=9999,
                date=date.today(),
                time=datetime.now().time(),
            )
            self.session.add(invalid_food_log)
            self.session.commit()

    def test_date_not_null_constraint(self):
        # Test that the date not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food_log.date = None
            self.session.commit()

    def test_user_id_not_null_constraint(self):
        # Test that the user_id not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food_log.user_id = None
            self.session.commit()

    def test_food_id_not_null_constraint(self):
        # Test that the food_id not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.food_log.food_id = None
            self.session.commit()

    def test_get_food_log_by_id(self):
        food_log = self.session.get(FoodLog, self.food_log.id)
        self.assertEqual(food_log.id, self.food_log.id)

    def test_get_all_food_logs_for_user(self):
        food_logs = (
            self.session.query(FoodLog).filter(FoodLog.user_id == self.user.id).all()
        )
        self.assertEqual(len(food_logs), 1)

    def test_get_food_logs_by_date(self):
        # Define a date for the test
        test_date = datetime.now().date()
        # Query for food logs on the test date
        food_logs = self.session.query(FoodLog).filter(FoodLog.date == test_date).all()
        # Check the result
        self.assertEqual(len(food_logs), 1)


class TestWorkoutRecommendation(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()
        # Create a workout recommendation
        self.workout = WorkoutRecommendation(
            workout_name="Test Workout",
            description="Test Description",
            exercise_type=1,
            duration=1.0,
            difficulty_level=1,
        )
        self.session.add(self.workout)
        self.session.commit()

    def test_workout_creation(self):
        # Test that the workout recommendation was created
        self.assertIsNotNone(self.workout.id)

    def test_workout_update(self):
        # Test that you can update the workout recommendation
        self.workout.workout_name = "Updated Workout"
        self.session.commit()
        self.assertEqual(self.workout.workout_name, "Updated Workout")

    def test_workout_delete(self):
        # Test that you can delete the workout recommendation
        self.session.delete(self.workout)
        self.session.commit()
        self.assertIsNone(self.session.get(WorkoutRecommendation, self.workout.id))

    def test_exercise_type_constraint(self):
        # Test that the exercise_type constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.exercise_type = 4
            self.session.commit()

    def test_duration_constraint(self):
        # Test that the duration constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.duration = 3.1
            self.session.commit()

    def test_difficulty_level_constraint(self):
        # Test that the difficulty_level constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.difficulty_level = 4
            self.session.commit()

    def test_workout_name_not_null_constraint(self):
        # Test that the workout_name not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.workout_name = None
            self.session.commit()

    def test_difficulty_level_not_null_constraint(self):
        # Test that the difficulty_level not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.difficulty_level = None
            self.session.commit()

    def test_duration_not_null_constraint(self):
        # Test that the duration not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.duration = None
            self.session.commit()

    def test_exercise_type_not_null_constraint(self):
        # Test that the exercise_type not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout.exercise_type = None
            self.session.commit()

    def test_get_workout_recommendation_by_id(self):
        workout_recommendation = self.session.get(
            WorkoutRecommendation, self.workout.id
        )
        self.assertEqual(workout_recommendation.id, self.workout.id)

    def test_get_workout_recommendations_by_condition(self):
        workout_recommendations = (
            self.session.query(WorkoutRecommendation)
            .filter(WorkoutRecommendation.difficulty_level > 1)
            .all()
        )
        self.assertEqual(len(workout_recommendations), 0)


class TestUserWorkout(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user workout
        self.user_workout = UserWorkout(
            exercise_type=1,
            description="Test Description",
            duration=1.0,
            difficulty_level=1,
        )
        self.session.add(self.user_workout)
        self.session.commit()

    def test_user_workout_creation(self):
        # Test that the user workout was created
        self.assertIsNotNone(self.user_workout.id)

    def test_user_workout_update(self):
        # Test that you can update the user workout
        self.user_workout.description = "Updated Description"
        self.session.commit()
        self.assertEqual(self.user_workout.description, "Updated Description")

    def test_user_workout_delete(self):
        # Test that you can delete the user workout
        self.session.delete(self.user_workout)
        self.session.commit()
        self.assertIsNone(self.session.get(UserWorkout, self.user_workout.id))

    def test_exercise_type_constraint(self):
        # Test that the exercise_type constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.exercise_type = 4
            self.session.commit()

    def test_duration_constraint(self):
        # Test that the duration constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.duration = 3.1
            self.session.commit()

    def test_difficulty_level_constraint(self):
        # Test that the difficulty_level constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.difficulty_level = 4
            self.session.commit()

    def test_excercise_type_not_null_constraint(self):
        # Test that the exercise_type not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.exercise_type = None
            self.session.commit()

    def test_description_not_null_constraint(self):
        # Test that the description not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.description = None
            self.session.commit()

    def test_duration_not_null_constraint(self):
        # Test that the duration not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.duration = None
            self.session.commit()

    def test_difficulty_level_not_null_constraint(self):
        # Test that the difficulty_level not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.user_workout.difficulty_level = None
            self.session.commit()

    def test_get_user_workout_by_id(self):
        user_workout = self.session.get(UserWorkout, self.user_workout.id)
        self.assertEqual(user_workout.id, self.user_workout.id)

    def test_get_user_workouts_by_condition(self):
        user_workouts = (
            self.session.query(UserWorkout).filter(UserWorkout.duration > 0.5).all()
        )
        self.assertEqual(len(user_workouts), 1)


class TestWorkoutLog(BaseTestCase):
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user, a user workout, and a workout recommendation
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.user_workout = UserWorkout(
            exercise_type=1,
            description="Test Description",
            duration=1.0,
            difficulty_level=1,
        )
        self.workout_recommendation = WorkoutRecommendation(
            workout_name="Test Workout",
            description="Test Description",
            exercise_type=1,
            duration=1.0,
            difficulty_level=1,
        )
        self.session.add(self.user)
        self.session.add(self.user_workout)
        self.session.add(self.workout_recommendation)
        self.session.commit()

        # Create a workout log entry
        self.workout_log = WorkoutLog(
            user_id=self.user.id,
            user_workout_id=self.user_workout.id,
            recommendation_id=None,
            calories_burned=200,
            heart_rate=80,
            date=date.today(),
        )
        self.session.add(self.workout_log)
        self.session.commit()

    def test_workout_log_creation(self):
        # Test that the workout log entry was created
        self.assertIsNotNone(self.workout_log.id)

    def test_workout_log_update(self):
        # Test that you can update the workout log entry
        self.workout_log.date = date.today() - timedelta(days=1)
        self.session.commit()
        self.assertEqual(self.workout_log.date, date.today() - timedelta(days=1))

    def test_workout_log_delete(self):
        # Test that you can delete the workout log entry
        self.session.delete(self.workout_log)
        self.session.commit()
        self.assertIsNone(self.session.get(WorkoutLog, self.workout_log.id))

    def test_user_id_foreign_key_constraint(self):
        # Test that the user_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_workout_log = WorkoutLog(
                user_id=9999,
                user_workout_id=self.user_workout.id,
                recommendation_id=None,
                calories_burned=200,
                heart_rate=80,
                date=date.today(),
            )
            self.session.add(invalid_workout_log)
            self.session.commit()

    def test_user_workout_id_foreign_key_constraint(self):
        # Test that the user_workout_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_workout_log = WorkoutLog(
                user_id=self.user.id,
                user_workout_id=9999,
                recommendation_id=None,
                calories_burned=200,
                heart_rate=80,
                date=date.today(),
            )
            self.session.add(invalid_workout_log)
            self.session.commit()

    def test_recommendation_id_foreign_key_constraint(self):
        # Test that the recommendation_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_workout_log = WorkoutLog(
                user_id=self.user.id,
                user_workout_id=None,
                recommendation_id=9999,
                calories_burned=200,
                heart_rate=80,
                date=date.today(),
            )
            self.session.add(invalid_workout_log)
            self.session.commit()

    def test_workout_recommendation_exclusive_constraint(self):
        # Test that the workout recommendation exclusive constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_workout_log = WorkoutLog(
                user_id=self.user.id,
                user_workout_id=self.user_workout.id,
                recommendation_id=self.workout_recommendation.id,
                calories_burned=200,
                heart_rate=80,
                date=date.today(),
            )
            self.session.add(invalid_workout_log)
            self.session.commit()

    def test_calories_burned_constraint(self):
        # Test that the calories_burned constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout_log.calories_burned = -1
            self.session.commit()

    def test_heart_rate_constraint(self):
        # Test that the heart_rate constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout_log.heart_rate = -1
            self.session.commit()

    def test_date_not_null_constraint(self):
        # Test that the date not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout_log.date = None
            self.session.commit()

    def test_user_id_not_null_constraint(self):
        # Test that the user_id not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.workout_log.user_id = None
            self.session.commit()

    def test_get_workout_log_by_id(self):
        workout_log = self.session.get(WorkoutLog, self.workout_log.id)
        self.assertEqual(workout_log.id, self.workout_log.id)

    def test_get_all_workout_logs_for_user(self):
        workout_logs = (
            self.session.query(WorkoutLog)
            .filter(WorkoutLog.user_id == self.user.id)
            .all()
        )
        self.assertEqual(len(workout_logs), 1)

    def test_get_workout_logs_by_condition(self):
        workout_logs = (
            self.session.query(WorkoutLog)
            .filter(WorkoutLog.calories_burned > 150)
            .all()
        )
        self.assertEqual(len(workout_logs), 1)


class TestGoal(BaseTestCase):
    # TODO: no not null tests
    def setUp(self):
        # Call the setUp method of the parent class to set up the test database
        super().setUp()

        # Create a user
        self.user = User(
            name="Test User",
            age=30,
            gender=1,
            weight=70.0,
            height=170.0,
            email="test@example.com",
            password="password",
        )
        self.session.add(self.user)
        self.session.commit()

        # Create a goal
        self.goal = Goal(
            user_id=self.user.id,
            description="Test Goal",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            goal_type=1,
        )
        self.session.add(self.goal)
        self.session.commit()

    def test_goal_creation(self):
        # Test that the goal was created
        self.assertIsNotNone(self.goal.id)

    def test_goal_update(self):
        # Test that you can update the goal
        self.goal.description = "Updated Goal"
        self.session.commit()
        self.assertEqual(self.goal.description, "Updated Goal")

    def test_goal_delete(self):
        # Test that you can delete the goal
        self.session.delete(self.goal)
        self.session.commit()
        self.assertIsNone(self.session.get(Goal, self.goal.id))

    def test_user_id_foreign_key_constraint(self):
        # Test that the user_id foreign key constraint is enforced
        with self.assertRaises(IntegrityError):
            invalid_goal = Goal(
                user_id=9999,
                description="Invalid Goal",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
                goal_type=1,
            )
            self.session.add(invalid_goal)
            self.session.commit()

    def test_goal_type_constraint(self):
        # Test that the goal_type constraint is enforced
        with self.assertRaises(IntegrityError):
            self.goal.goal_type = 4
            self.session.commit()

    def test_start_date_before_end_date_constraint(self):
        # Test that the start_date_before_end_date constraint is enforced
        with self.assertRaises(IntegrityError):
            self.goal.start_date = date.today() + timedelta(days=1)
            self.goal.end_date = date.today()
            self.session.commit()

    def test_description_not_null_constraint(self):
        # Test that the description not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.goal.description = None
            self.session.commit()

    def test_user_id_not_null_constraint(self):
        # Test that the user_id not null constraint is enforced
        with self.assertRaises(IntegrityError):
            self.goal.user_id = None
            self.session.commit()

    def test_get_goal_by_id(self):
        goal = self.session.get(Goal, self.goal.id)
        self.assertEqual(goal.id, self.goal.id)

    def test_get_all_goals_for_user(self):
        goals = self.session.query(Goal).filter(Goal.user_id == self.user.id).all()
        self.assertEqual(len(goals), 1)

    def test_get_goals_by_condition(self):
        test_date = datetime.now().date() - timedelta(days=1)
        goals = self.session.query(Goal).filter(Goal.end_date > test_date).all()
        self.assertEqual(len(goals), 1)


if __name__ == "__main__":
    unittest.main()
