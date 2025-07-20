import streamlit as st
import fastf1
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties 
import pandas as pd 
import numpy as np
import warnings
warnings.filterwarnings("ignore")   


st.sidebar.title("About")
SESSION_MAPPING = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Qualifying": "Q",
    "Race": "R",
    "Sprint": "S",  # Sprint Race
    "Sprint Shootout": "SS",  # Sprint Qualifying
    "Sprint Qualifying": "SS"  # Alternative name
}

F1_BOLD_PATH = r"D:\PYTON PROGRAMMING\PYTHON FILES\Data-Visualization-Using-Python\STREAMLIT & PANEL\F1 RACE ANALYSIS PROJECTS\F1 Font\Formula1-Bold_web_0.ttf"
F1_REGULAR_PATH = r"D:\PYTON PROGRAMMING\PYTHON FILES\Data-Visualization-Using-Python\STREAMLIT & PANEL\F1 RACE ANALYSIS PROJECTS\F1 Font\Formula1-Regular_web_0.ttf"

# 1. Font Loading with Fallback
try:
    f1_bold = FontProperties(fname=F1_BOLD_PATH)
    f1_regular = FontProperties(fname=F1_REGULAR_PATH)
    st.toast("✅ F1 Fonts loaded successfully!")
except:
    # Fallback to default fonts if F1 fonts not found
    f1_bold = FontProperties(weight='bold')
    f1_regular = FontProperties()
    st.warning("❌ F1 fonts not found - using system defaults")

# 2. Get Event Schedule with Sprint Sessions
year = st.sidebar.selectbox("Year", list(reversed(range(2018, 2026))))
schedule = fastf1.get_event_schedule(year)

# 3. Modified Event Selection with Sprint Support
event_name = st.sidebar.selectbox("Event", schedule['EventName'].tolist())
event_data = schedule[schedule['EventName'] == event_name].iloc[0]

# Get ALL available sessions (including sprints if they exist)
available_sessions = [
    session for session in 
    event_data[['Session1', 'Session2', 'Session3', 'Session4', 'Session5']] 
    if pd.notna(session)
]

# 4. Session Selection with Sprint Options
session_type = st.sidebar.selectbox("Session", available_sessions)

# 5. Convert to FastF1 Session Code
session_code = SESSION_MAPPING.get(session_type)
if not session_code:
    st.toast(f"❌ Unsupported session type: {session_type}")
    st.stop()

# 6. Load Session (with error handling)
try:
    session = fastf1.get_session(year, event_name, session_code)
    session.load()
    df = session.laps
    results = session.results.sort_values(by='Abbreviation')
    st.toast(
    f"✅ Successfully loaded {event_name} {session_type} ({session_code})", 
    icon="🏎️"
    )
except Exception as e:
    st.error(f"❌ Failed to load session: {str(e)}")
    st.stop()
    

