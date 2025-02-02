import streamlit as st
import altair as alt
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time

from utils import *

# Set Up Connection

username = 'root'
password = 'root'
host = 'localhost'
port = '18123'
database = 'clickhouse'

try:
    engine = create_engine(f'clickhousedb://{username}:{password}@{host}:{port}/{database}')
    session = sessionmaker(bind=engine)()

    print("Connected to Clickhouse!")
except Exception as e:
    print("Error while connecting to Clickhoust " + str(e))

# Set Page Configuration
st.set_page_config(layout="wide",
                   page_title="Baller Market Value Analysis",
                   page_icon="⚽")

st.title("⚽ This is The Summary of Top 100 Baller With Highest Market Value ")

# Set Dashboard Conigurtion

now = datetime.now()
dt_string = now.strftime("%d %B %Y %H:%M:%S")
st.write(f"Last update: {dt_string}")

if not "sleep_time" in st.session_state:
    st.session_state.sleep_time = 5

if not "auto_refresh" in st.session_state:
    st.session_state.auto_refresh = True

#
mapping = {
    "1 hour": {"period": "60", "granularity": "minute", "raw": 60},
    "30 minutes": {"period": "30", "granularity": "minute", "raw": 30},
    "10 minutes": {"period": "10", "granularity": "minute", "raw": 10},
    "5 minutes": {"period": "5", "granularity": "minute", "raw": 5}
}

with st.expander("Configure Dashboard", expanded=True):
    left, right = st.columns(2)

    with left:
        auto_refresh = st.checkbox('Auto Refresh?', st.session_state.auto_refresh)

        if auto_refresh:
            number = st.number_input('Refresh rate in seconds', value=st.session_state.sleep_time)
            st.session_state.sleep_time = number

    with right:
            time_ago = st.radio("Time period to cover", mapping.keys(), horizontal=True, key="time_ago")

try:
    st.header("Baller with Hihgest Market Value ... 🐐" )

    minute = mapping[time_ago]["period"]
    print(str(minute))

    query = f'''select 
    player_name, 
    position, 
    club_name, 
    country_name, 
    age, 
    market_value
    from `clickhouse`.db_football_player_view
    where source_collected >=  insert_time_clickhouse -  INTERVAL {minute} MINUTE ;'''

    df = pd.read_sql(query, engine)
    df.style.format('{:,}')
    df = df.sort_values('market_value', ascending=False).head(100)

    df['age_cluster'] = pd.cut(df["age"], bins=[16, 20, 25, 30, 35, 40], 
                            labels=["16-20", "21-25", "26-30", "31-35", "36-40"], right=True)

    metric1, metric2, metric3, metric4 = st.columns(4)

    # Most Valueable Player
    highest_market_value = df['market_value'].max()
    player_name = df[df['market_value'] == highest_market_value]['player_name'].reset_index(drop=True)[0]

    metric1.metric(
        label="Most Valueable Player",
        value=(player_name),
    )

    metric2.metric(
        label="Market Value",
        value=(f'{round(highest_market_value/1000000000000, 2)} Trillion Rupiah'),
    )

    metric3.metric(
        label="Club Name",
        value=(df[df['player_name'] == player_name]['club_name'].reset_index(drop=True)[0]),
    )

    metric4.metric(
        label="Country Name",
        value=(df[df['player_name'] == player_name]['country_name'].reset_index(drop=True)[0]),
    )

    st.divider()

    st.header("Lets Count ... 🧮" )

    tab1, tab2, tab3 = st.columns(3)

    # top club
    df_club = df.groupby('club_name').agg({
        'player_name' : 'count',
    }).reset_index().sort_values('player_name', ascending=False).head(5)

    with tab1:
        create_bar_chart(df_club, 'player_name', 'club_name', 'Top 5 Total Player by Club', 'Number of Players', 'Club Name', 'teal')

    # top country
    df_country = df.groupby('country_name').agg({
        'player_name' : 'count',
    }).reset_index().sort_values('player_name', ascending=False).head(5)

    with tab2:
        create_bar_chart(df_country, 'player_name', 'country_name', 'Top 5 Total Player by Country', 'Number of Players', 'Country Name', 'teal')

    # top position
    df_position = df.groupby('position').agg({
        'player_name' : 'count',
    }).reset_index().sort_values('player_name', ascending=False).head(5)

    with tab3:
        create_bar_chart(df_position, 'player_name', 'position', 'Top 5 Total Player by Position', 'Number of Players', 'Position', 'teal')

    st.divider()

    st.header("Market Value Analysis ... 💻" )

    col1, col2, col3 = st.columns(3)

    # top club
    df_club = df.groupby('club_name').agg({
        'market_value' : 'mean',
    }).reset_index().sort_values('market_value', ascending=False).head(5)
    df_club['market_value'] = round((df_club['market_value']/1000000000000), 2)

    with col1:
        create_bar_chart(df_club, 'market_value', 'club_name', 'Top 5 Highest Total MV by Club', 'Market Value (Trillion Rp)', 'Club Name', 'steelblue')

    # top country
    df_country = df.groupby('country_name').agg({
        'market_value' : 'mean',
    }).reset_index().sort_values('market_value', ascending=False).head(5)
    df_country['market_value'] = round((df_country['market_value']/1000000000000), 2)

    with col2:
        create_bar_chart(df_country, 'market_value', 'country_name', 'Top 5 Highest Total MV by Country', 'Market Value (Trillion Rp)', 'Country Name', 'steelblue')

    # top position
    df_position = df.groupby('position').agg({
        'market_value' : 'mean',
    }).reset_index().sort_values('market_value', ascending=False).head(5)
    df_position['market_value'] = round((df_position['market_value']/1000000000000), 2)

    with col3:
        create_bar_chart(df_position, 'market_value', 'position', 'Top 5 Highest Total MV by Position', 'Market Value (Trillion Rp)', 'Position', 'steelblue')

    st.divider()

    st.header(f"Do You Agree That {player_name} is A Baller With Highest MV ??")

    st.divider()

except Exception as e:
    st.divider()
    st.header('Still Waiting For The Data ....')