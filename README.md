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

### Food
assume that there is a pre populated list

why did I not pick name as the PK?

- workout tables — how to do these logs
    - stream line with recommendations? or is this unnecessary?
- how to connect activities to goal success
- food logs — reusability


many queries per table

few transactions for table


### optimization

 optimize FKs by adding indexes to them to prevent costly join operations

 backrefs also speed up joins with user

 primary key values should not be updated

 talk about acid for committing data?
 
 constraints do have a cost


 ### file structure