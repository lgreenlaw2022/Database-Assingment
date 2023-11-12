# Database Assignment

## Run instructions


> Provide a detailed description of the Health and Fitness Tracking App. Describe its primary objectives, target audience, and the specific health and fitness metrics it will track, including sleep data. Explain how the app will benefit users in achieving their fitness goals and maintaining a healthy lifestyle.


## Health and Fitness Tracking App Description

### Primary Objectives
Store users health and sleep data so they can record important metrics and retrieve reports of their past behavior. 

### Target Audience
An every day person interested in monitoring their nutrition, exercise, and sleep. This app assumes that users have a smart device uploading data. For example, the health metrics of heart rate, blood pressure, and steps are uploaded all together automatically by the device at certain times of day. The app helps users track their progress and analyze their performance by setting goals and tracking actions towards those goals. 

### Metrics Tracked
TODO: TO ASK: feels like I am just listing out the schema here
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
Each food is logged independently. TODO: update and check
1. calories
2. food category (protein, carb, fat, veggie, fruit)

#### Workout Tracking
1. workout type (cardio, strength, flexibility)
2. duration
3. calories burned
4. average heart rate
5. difficulty level

#### Goal Tracking
TODO: update and check
1. goal description
2. start date
3. end date
4. status (not started, in progress, complete)


### App Benefits
This app allows people to quickly check their health metrics. It assumes that some sort of health device is uploading the time stamped data frequently to the tables for health metrics, sleep, and workouts. Users can also manually log their behaviors and their nutrition. This app is powerful because it allows users to set health goals and track their progress towards them. TODO: explain exactly how the goal setting + tracking works. It also makes exercising easier by filtering and offering workout recommendations. This makes it easier to maintain a healthy lifestyle. The nutrition log also stores past foods the user has eaten, allowing them to quickly log new entries to the nutrition log (TODO: true?)



## Data Requirements
> Identify the key data elements that the app needs to store and manage. This includes user data, workout information, nutrition logs, sleep patterns, and any other relevant health metrics. Discuss the relationships between different data elements and the importance of capturing these data points for the success of the application

### Users
The application needs to allow for many different users each with their own records and log in information. The users table includes all of their log in information and some basic health information like height and weight. Because log entries are connected to the user, `user_id` is a foreign key in most of the other tables since there is a many (entries) to 1 (user) relationship. 

### Health Metrics
Users can have multiple overview health metrics reported by their smart devices each day. All users can have many records (but each record is unique). These records include heart rate, step count, stand hours and blood pressure (split up into diastolic and systolic). Note that the heart rate is resting heart rate as the workout logs will give the exercise heart rates. The assumption is that these metrics will be uploaded all together at least once a day by whatever health tracking devices the user uses. All of these values are constrained to positive numbers. It is possible for a few of the metrics to be missing, but the date and user id are required (this could show an issue with the updating). These are basic data points users may want to track over time (norms and irregularities).

### Sleep
Users have 1 sleep record every night (assuming their data is updated reliably). The quality, length, and exact start and end times are measured. This table requires the foreign key connection to the user id. This table is technically not up to 3rd form because duration is a transitive dependency of start time and end time. However, I argue that on insertion, the processor can calculate the duration from those times. I chose to include this field in the table because I think it is a critical value of interest to many users. Many people are going to be most interest in tracking how many hours of sleep they have been getting and the quality, rather than checking the exact start and end times. If I did not store duration, for every day in the query, the duration would have to be calculated. This is more expensive than calculating the value before storing it. Additionally, many sleep monitors will upload these data independently. 

### Food Tracking
This system uses a food database. The assumption is there is a prepopulated list for users to select the food from. Users can also add items to this table of foods if necessary, tracking their name, category (food, vegetable etc) and number of calories. The goal is to help users track their food consumption and nutrition in a log. The foods can be selected from a drop down showing the food name (ensuring data normalization). On submit, the food is automatically updated to the log table which connects the user id with the food id and the date of the entry. The log table allows us to sort by user or food (both foreign keys). We can also isolate specific characteristics of the foods users have eaten via the `food_id` FK. For example, get the number of calories they have eaten today or how many servings of vegetables they eat on average every day in the past week. 

I did not make the food name a PK in the food table because it is possible for the name to be edited (eg. a typo on entry or maybe an existing food is rebranded with a new name). I do have the unique constraint to make sure only one entry of a specific food in the food table. Strings are also more expensive to process as a FK. Thus, I decided to add the surrogate, integer id column as the PK. 

### Workout Tracking

Users can add their own workouts or do one of the workouts from the recommendations table. User's can query for a workout according to the length, exercise type, and difficulty. They could also do the same workout again by searching the name. This allows user to quickly find a workout to their needs and add it to their workout log. The workout log either connects to one of the user workouts or one of the recommended workouts. 

There is also user workout table. The workout log connects the user workout to the user id. The user workout and workout recommendation tables are separate because each user may have very specific workouts with specialized descriptions that should not be included as recommendations. Further because there is a many to many relationship between the user and both workout tables, I do not want to keep the user id connected to a combined workouts table (recommendations + user's workouts). It is easier to query from the workout log based on user than having to check if an entry in a combined workout log is a user workout or a recommendation. Thus, while the tables are very similar, I have defined them separately to provide clarity in the code and make the queries simpler.

The workout log then holds the user's id and either an id for a user defined workout or one of the ids for a recommended work out. There is a constraint on these columns so that only 1 can be NOT NULL at a time. This allows me to show the relationship between the user and their workout in a streamlined way. Further, this table stores the stats that are not specific to the details of the workout. These are the calories burned and the average heart rate. Since these are specific to the user and the workout, they are in the relational table. These are data points people will want. For example, someone may want to subtract the number of calories they burned that day from the number of calories they ate that day to see if they are on track to reach a goal.



### optimization

optimize FKs by adding indexes to them to prevent costly join operations

backrefs also speed up joins with user
- You don't necessarily need both backrefs. A backref is a convenient feature in SQLAlchemy that adds a new property to the other class in a relationship. It's a way to navigate from one side of the relationship to the other.
- If you have a WorkoutLog instance and you want to get the associated WorkoutRecommendation, you would use the workout_recommendation backref. If you have a WorkoutRecommendation instance and you want to get all associated WorkoutLog instances, you would use the workout_logs backref.

primary key values should not be updated

talk about acid for committing data?

constraints do have a cost

why did I not pick (workout? food?) name as the PK?

without indexes: Query runtime: 3.5144259929656982 seconds

after date composite indexes: Query runtime: 2.2841548919677734 seconds

QUERY DEBUGGING:
USER Query runtime: 4.490666627883911 seconds
HEALTH METRICS Query runtime: 4.516571998596191 seconds
SLEEP runtime: 4.547794342041016 seconds
FOOD Query runtime: 4.593246221542358 seconds
WORKOUT Query runtime: 4.636799573898315 seconds
GOAL Query runtime: 4.646570444107056 seconds
TOTAL Query runtime: 4.646673679351807 seconds


>  I propose ONLY adding a constraint where and when it is truly and provably necessary. That way databases are allowed to focus just on storing and retrieving data, which is the role they truly excel at.


### file structure