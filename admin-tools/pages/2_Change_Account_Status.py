import pandas as pd
from pandas import json_normalize #package for flattening json in pandas df
import streamlit as st
from datetime import datetime, date
import json
import requests
import hmac

st.title('Racket Admin Tools')

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

st.header('User Status Change')
st.write(' ')
st.write(' ')

st.subheader('Current Users of Racket')
st.write(' ')
st.write(' ')


# Get the current list of Racket users
response = requests.get(st.secrets['users_endpoint'])
json_response = response.json()

df = pd.json_normalize(json_response)

df.rename(
    columns={
    'id':'racket_user_id',
    'createdAt':'created_at',
    'username':'twitter_username',
    'twitterId':'twitter_id',
    'suspend':'is_suspended'
    }, 
    inplace=True
)


# Reorder the columns in the dataframe
df = df[['racket_user_id', 'twitter_username', 'twitter_id', 'created_at', 'is_suspended']]

# Fill all none values with empty strings
df.fillna('', inplace=True)

# Put three streamlit filters side by side
filter1, filter2 = st.columns(2)

with filter1:
    twitter_username = st.multiselect('Twitter Username', df['twitter_username'].sort_values(ascending=True).unique())
with filter2:
    is_suspended = st.selectbox('Is Suspended', df['is_suspended'].sort_values(ascending=True).unique(),index=None)


# Conditionally filter the dataframe based on the user input, but only if the user input is not empty
if twitter_username and is_suspended:
    df_filtered = df[df['twitter_username'].isin(twitter_username) & df['is_suspended'] == is_suspended]
elif twitter_username:
    df_filtered = df[df['twitter_username'].isin(twitter_username)]
elif is_suspended:
    df_filtered = df[df['is_suspended'] == is_suspended]
else:
    df_filtered = df


st.write(' ')
st.write(' ')

st.dataframe(df_filtered,use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Change Account Status')
st.write('Enter a comma separated list of Twitter usernames to suspend or reinstate them.')

def change_account_status(account_change, twitter_usernames):

    # Concatenate the twitter usernames into a string using commas
    processed_list_of_twitter_usernames = [x.strip(' ') for x in twitter_usernames.split(',')]
    twitter_usernames_string = '&'.join(processed_list_of_twitter_usernames)

    if account_change == 'Suspend':
        requests.post(st.secrets['suspend_endpoint'] + twitter_usernames_string)
        # print(st.secrets['suspend_endpoint'] + twitter_usernames_string)
    elif account_change == 'Reinstate':
        requests.post(st.secrets['reinstate_endpoint'] + twitter_usernames_string)
        # print(st.secrets['reinstate_endpoint'] + twitter_usernames_string)
    else:
        st.error('This is an error', icon="🚨")

    

buttons, space1 = st.columns(2)

with buttons:
    twitter_usernames = st.text_area('Twitter Usernames',placeholder='')

    account_change = st.selectbox('Account Change', options=['Suspend', 'Reinstate'], index=None)

    st.write(' ')
    st.button('Update Account Status', on_click=change_account_status, args=(account_change, twitter_usernames),use_container_width=True)