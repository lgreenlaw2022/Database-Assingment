# Database Assignment

## Run instructions
```
python3 -m venv venv
venv\bin\activate.bat
pip3 install -r requirements.txt
python3 init_db.py
python3 insert_data.py
python3 query_data.py

<!-- Test -->
python3 test.py
```

### Important Files
`init_db.py`: creates the database and its models

`insert_data.py`: adds fake data to each of the tables

`query_data.py`: demonstrates how to query the database to get metrics and reports to track user's progress

`db_session.py`: creates a SQLAlchemy Session using the predefined `init_db` engine. It ensures consistent session configuration across all database interactions and allows control over the session scope, which can be adjusted to either use a new session for each request or share a session across multiple requests. This is used in `insert_data.py`.

`schema.png`: a visual representation of my database schema created from `schema.dot`

`tests.py`: runs a unit test suite for each model, verifying CRUD operations and constraints (including FK constraints). 

<!-- TODO: include transactions file? -->
## Health and Fitness Tracking App Description

### Primary Objectives
Store users health, fitness, nutrition and sleep data so they can record important metrics and retrieve reports of their past behavior. 

### Target Audience
An every day person interested in monitoring their nutrition, exercise, and sleep. This app assumes that users have a smart device uploading data. For example, the health metrics of heart rate, blood pressure, and steps are uploaded all together automatically by the device at certain times of day. The app helps users track their progress and analyze their performance by setting goals and tracking actions towards those goals. 

### Metrics Tracked

All of these metrics are tracked for the specific user and include a time stamp. 

#### Basic health metrics
1. heart rate
2. step count
3. stand hours
4. blood pressure

#### Sleep Tracking
1. hours slept
2. fall asleep time
3. wake up time
4. sleep quality (poor to excellent)

#### Nutrition Tracking
This includes a database of foods.
1. calories
2. food category (protein, carb, fat, veggie, fruit)

Users then log food to their nutrition log:
1. food name
2. date
3. time

#### Workout Tracking
Users can create their own workouts or select from recommended workouts. The workout is summarized with:
1. workout type (cardio, strength, flexibility)
2. duration
3. difficulty level (easy to hard)

A log then indicates which workout was completed and the metrics of that workout
1. average heart rate
2. calories burned
3. date

#### Goal Tracking
1. goal description
2. start date
3. end date
4. goal type (fitness, nutrition, sleep)


### App Benefits
This app allows people to quickly check their health metrics. It assumes a health device is uploading the time stamped data frequently to the tables for health metrics, sleep, and workouts. Users can also manually log their workouts and their nutrition. This app is powerful because it allows users to set health goals and track their progress towards them. It also makes exercising easier by filtering and offering workout recommendations. The nutrition log also holds the food database allowing the user allowing them to quickly log new entries to the nutrition log. Accessing historical data can help them see their progress and stay motivated to continue working towards their goals. 


## Data Requirements

### Users
The application needs to allow for many different users each with their own records and log in information. The users table includes all of their log in information and some basic health information like height and weight. User can also modify their weight if they want to track a weight loss goal. Because log entries are connected to the user, `user_id` is a foreign key in most of the other tables since there is a many (entries) to 1 (user) relationship. 

### Health Metrics
Users can have multiple overview health metrics reported by their smart devices. All users can have many records (but each record is unique). These records include heart rate, step count, stand hours and blood pressure (split up into diastolic and systolic to maintain atomicity). Note that the heart rate is resting heart rate as the workout logs will give the exercise heart rates. The assumption is that these metrics will be uploaded all together at least once a day by whatever health tracking devices the user uses. All of these values are constrained to positive numbers. It is possible for a few of the metrics to be missing, but the date and user id are required (this could show an issue with the updating). These are basic data points users may want to track over time and could indicate any health issues.

### Sleep
Users have 1 sleep record every night (assuming their data is updated reliably). The quality, length, and exact start and end times are measured. This table requires the foreign key connection to the user id. This table is technically 2nd form because duration is a transitive dependency of start time and end time. However, I argue that on insertion, the data processor can calculate the duration from those times. I chose to include this field in the table because I think it is a critical value of interest to many users. Many people are going to be most interested in tracking how many hours of sleep they have been getting and the quality, rather than checking the exact start and end times. If I did not store duration, for every day in the query, the duration would have to be calculated on each request. This is more expensive than calculating the value before storing it. Additionally, many sleep monitors will upload these data independently. 

### Food Tracking
This system uses a food database. The assumption is there is a prepopulated list for users to select the food from. Users can also add items to this table of foods if necessary, tracking their name, category (food, vegetable etc) and number of calories. The goal is to help users track their food consumption and nutrition in a log. The foods could be selected from a drop down showing the food name (ensuring data normalization). On submit, the food is automatically updated to the log table which connects the user id with the food id and the date of the entry. The log table allows us to sort by user or food (both foreign keys). We can also isolate specific characteristics of the foods users have eaten via the `food_id` FK. For example, query the number of calories they have eaten today or how many servings of vegetables they eat on average every day in the past week. 

I did not make the food name a PK in the food table because it is possible for the name to be edited (eg. a typo on entry or maybe an existing food is rebranded with a new name). I do have the unique constraint to make sure only one entry of a specific food in the food table. Strings are also more expensive to process as a FK. Thus, I decided to add the surrogate, integer id column as the PK. 

### Workout Tracking
Users can add their own workouts or do one of the workouts from the recommendations table. User's can query for a workout according to the length, exercise type, and difficulty. They could also do the same workout again by searching the name. This allows user to quickly find a workout to their needs and add it to their workout log. The workout log either connects to one of the user workouts or one of the recommended workouts. 

There is also user workout table. The user workout and workout recommendation tables are separate because each user may have very specific workouts with specialized descriptions that should not be included as recommendations. Further because there is a many to many relationship between the user and both workout tables, I do not want to keep the user id connected to a combined workouts table (recommendations + user's workouts). It is easier to query from the workout log based on user than having to check if an entry in a combined workout log is a user workout or a recommendation. Thus, while the tables are similar, I have defined them separately to provide clarity in the code and make the queries simpler.

The workout log then holds the user's id and either an id for a user defined workout or one of the ids for a recommended work out. There is a constraint on these columns so that only 1 can be NOT NULL at a time. This allows me to show the relationship between the user and their workout in a streamlined way. Further, this table stores the stats that are not specific to the details of the workout. These are the calories burned and the average heart rate. Since these are specific to the user and the workout, they are in the relational table. These are data points people will want. For example, someone may want to subtract the number of calories they burned that day from the number of calories they ate that day to see if they are on track to reach a goal.

### Goals
Users can track their goals to see what goals they have completed and which are in progress. This requires a FK to the user id. The start and end dates may be most important because we expect people to be looking for goals of a certain status (done, in progress, not started). This table allows users to quickly search through their information. The goal type also helps connect the goal to the metrics relevant to the goal.

### Data population
The data insertions are completed using the python Faker library. This library generates realistic names, passwords, etc. While sometimes the faked categories do not quite align, this library makes the queries more demonstrative of the application's features. I use an extension of the Faker package, FoodFaker, to get even more realistic entries into the food table. This library also has limitations but made my data insertions more realistic. 

The application only generates 25 users because each user has a significant amount of entries. For example, a user has 3 entires per day in a 30 day period in their food log. This makes the Food Log table over 2,000 entries long. For thorough testing of performance, much larger batches of data can be added. Note that running the insertions file takes long time. Approximately 1/3 of the load time comes just from importing and instantiating a faker provider. 

Insertions can also be slowed down by constraints. Many columns in my tables have constraints to ensure data integrity and that the accesses data is retrievable. For example, "age >= 0". For many of these values, with an actual front end, they would be validated and normalized before the data is submitted (drop down menus, input field restrictions). We can also assume that the smart devices as well will only upload valid data (e.g.heart rate > 0). However, because I am inserting bulk data manually, these constraints make sure that I have not mistakenly added invalid data. When implemented, some of these CheckConstraints should be removed because they do slow down insertions. Only the values most critical to the database or one's that are not enforced in a different level of the user experience will remain. 

### Optimization

#### Indexing

1. Foreign keys

SQLAlchemy automatically indexes primary key columns. I added indexes to the foreign key columns, usually the `user_id` FK. This is important because these columns (especially user id) are frequently part of the query. 

When you perform a join operation between two tables, the database needs to look up the foreign key in the related table. If the foreign key column is not indexed, this lookup operation can be slow because the database needs to scan the entire table. If the foreign key column is indexed, the database can use the index to find the related records more quickly, which can significantly speed up the join operation.

2. Composite indexes

Looking at my queries, it is clear I frequently want to limit my search by time or date (eg. "how many workouts for user 1 in the last week" etc). This could be expensive to look up because even if the user_id is indexed the logs will have a huge number of entries. Finding the correct date is expensive. Thus, for the tables holding both a user id and a date, I added a composite index (beginning with user id to be most efficient).

This is helpful beyond the index on user id because the database can use the index to quickly find records that match both the user_id and date, which can be significantly faster than using the user_id index alone and scanning for date. This is important because I can filter on both columns as once.

3. Other indexes
I also added index on the workout specification columns of workout recommendations (duration, type, difficulty). These are important because we expect users to be filtering the recommended workouts to fit their conditions. As the number of user grows, I will want them to be able to handle their filtering calls more efficiently. 

Overall, as the database grows, it will be important to keep testing if the storage space and write operations are taxed by maintaining these indexes. It is possible for the creating and storing the indexes to take up too much space. This may outweigh the benefit of increased query run time. Frequent assessments will be required.

#### backrefs
Using a backref provides a more convenient way to navigate relationships between tables and retrieve related objects. They can also make my code more readable. Instead of having to write a separate query, I can directly access the characteristic of a user or workout entry (etc) as if it were a property of the instance. 

Some examples in my code are.

``` python
user_workout = session.query(UserWorkout).filter(UserWorkout.id == workout_log.user_workout_id).first()
```
is simplified to be

``` python
if workout_log is not None:
    user_workout = workout_log.user_workout  # uses backref
```

and 
``` python
goals = session.query(Goal).filter(Goal.user_id == user1.id).all()
```
can be expressed as

``` python
goals = user1.goals
```
<!-- TODO: talked about acid for committing data? -->




