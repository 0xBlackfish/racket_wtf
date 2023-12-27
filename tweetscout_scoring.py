import pandas as pd
import requests
import os
from datetime import date, datetime

# Import environment variables
racket_user_api_key = os.environ.get('RACKET_USER_API_KEY')
tweetscout_api_key = os.environ.get('TWEETSCOUT_API_KEY')


# Determine the current datetime
now = datetime.now()


# Convert the current datetime into a string
now_string = now.strftime("%Y-%m-%dT%H-%M-%S")


# Function to score users via Tweetscout API
def score_users(username):

    APIKEY = tweetscout_api_key
    HEADERS = {
        "ApiKey": APIKEY
    }
    
    response_score = requests.get(url="https://api.tweetscout.io/api/score/{0}".format(username), headers=HEADERS)
    json_score = response_score.json()
    
    
    try:
        print(datetime.now(), username, json_score['score'])
        score = json_score['score']
    except:
        print(datetime.now(), username, 0)
        score = 0
    
    return score


# Make a call to the Racket User Reports API
racket_user_report_response = requests.get('https://racket.wtf/api/reportUsers?key={0}'.format(racket_user_api_key))

# Convert the Racket User Reports response to JSON
racket_user_report_json_response = racket_user_report_response.json()

# Read this json into a pandas dataframe
df_racket_users = pd.json_normalize(racket_user_report_json_response)

# Filter out users who are already suspended
df_racket_users_filtered = df_racket_users[~df_racket_users['suspended']]


# Create a new column in the dataframe with the Tweetscout score
df_racket_users_filtered['tweetscout_score'] = df_racket_users_filtered['username'].apply(score_users)


# Export the dataframe to a CSV
df_racket_users_filtered.to_csv('{}-racket_users.csv'.format(now_string), index=False)
