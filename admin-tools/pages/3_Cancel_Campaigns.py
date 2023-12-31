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

st.header('Campaign Cancellation')
st.write(' ')
st.write(' ')

st.subheader('Current Posts on Campaign Board')
st.write(' ')
st.write(' ')

# Get the current posts on the campaign board
response = requests.get(st.secrets['campaigns_endpoint'])
json_response = response.json()

df = pd.json_normalize(json_response)

df.rename(
    columns={
    'id':'campaign_id',
    'type':'campaign_type',
    'bidPrice':'bid_price',
    'desiredEngagements':'desired_engagements',
    'bidTotal':'bid_total',
    'bidTotalUnsettled':'bid_total_unsettled',
    'promotedTweet':'promoted_tweet',
    'promotedAccountUsername':'promoted_account_username',
    'promotedTweetAuthorUsername':'promoted_tweet_author_username',
    'createdBy.username':'created_by_username',
    }, 
    inplace=True
)

df['promoted_account_username'].fillna(df['promoted_tweet_author_username'], inplace=True)

# Put two streamlit filters side by side
filter1, filter2, filter3 = st.columns(3)

with filter1:
    promoted_user = st.multiselect('Promoted User', df['promoted_account_username'].sort_values(ascending=True).unique())
with filter2:
    created_by_username = st.multiselect('Campaign Creator', df['created_by_username'].sort_values(ascending=True).unique())
with filter3:
    campaign_type = st.multiselect('Campaign Type', df['campaign_type'].sort_values(ascending=True).unique())

# Conditionally filter the dataframe based on the user input, but only if the user input is not empty
if promoted_user and created_by_username and campaign_type:
    df_filtered = df[df['promoted_account_username'].isin(promoted_user) & df['created_by_username'].isin(created_by_username) & df['campaign_type'].isin(campaign_type)]
elif promoted_user and created_by_username:
    df_filtered = df[df['promoted_account_username'].isin(promoted_user) & df['created_by_username'].isin(created_by_username)]
elif promoted_user and campaign_type:
    df_filtered = df[df['promoted_account_username'].isin(promoted_user) & df['campaign_type'].isin(campaign_type)]
elif created_by_username and campaign_type:
    df_filtered = df[df['created_by_username'].isin(created_by_username) & df['campaign_type'].isin(campaign_type)]
elif promoted_user:
    df_filtered = df[df['promoted_account_username'].isin(promoted_user)]
elif created_by_username:
    df_filtered = df[df['created_by_username'].isin(created_by_username)]
elif campaign_type:
    df_filtered = df[df['campaign_type'].isin(campaign_type)]
else:
    df_filtered = df


st.write(' ')
st.write(' ')

df_display = df_filtered[['campaign_id','campaign_type','bid_price','desired_engagements','bid_total','bid_total_unsettled','promoted_tweet','promoted_account_username','created_by_username']]

st.dataframe(df_display,use_container_width=True)

st.write(' ')
st.write(' ')

st.subheader('Cancel Campaigns')
st.write('Enter a comma separated list of Campaign IDs to cancel them.')

def cancel_campaigns(campaign_ids):

    # Concatenate the campaign IDs into a string using ampersands
    processed_list_of_campaign_ids = [x.strip(' ') for x in campaign_ids.split(',')]
    campaign_ids_string = '&'.join(processed_list_of_campaign_ids)

    requests.post(st.secrets['cancel_endpoint'] + campaign_ids)

button, space1 = st.columns(2)

with button:
    campaign_ids = st.text_area('Campaign IDs',placeholder='Campaign IDs')
    st.button('Cancel Campaigns', on_click=cancel_campaigns(campaign_ids),use_container_width=True)