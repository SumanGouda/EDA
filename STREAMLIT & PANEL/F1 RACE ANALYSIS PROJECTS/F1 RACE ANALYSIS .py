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
# year = st.sidebar.selectbox("Year", list(reversed(range(2018, 2026))), index=0, format_func=lambda x: "Select Year" if x == "" else x)
year_options = [""] + list(reversed(range(2018, 2026)))

year = st.sidebar.selectbox(
    "Year",
    year_options,
    index=0,
    format_func=lambda x: "Select Year" if x == "" else str(x)  # Convert to string for safety
)

if year:
    schedule = fastf1.get_event_schedule(year)
    event_name = st.sidebar.selectbox("Event", schedule['EventName'].tolist())

    # 3. Modified Event Selection with Sprint Support
    if event_name:
        event_data = schedule[schedule['EventName'] == event_name].iloc[0]

        # Get ALL available sessions (including sprints if they exist)
        available_sessions = [
            session for session in 
            event_data[['Session1', 'Session2', 'Session3', 'Session4', 'Session5']] 
            if pd.notna(session)
        ]
        available_sessions = [""] + available_sessions
        # 4. Session Selection with Sprint Options
        session_type = st.sidebar.selectbox(
            "Session", 
            available_sessions,
            index = 0,
            format_func=lambda x: "Select Session" if x == "" else str(x)
        )
        
        if session_type:
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
                
                # 7. Plot the Graph
                pivot_df = df.pivot_table(index='Driver', columns='LapNumber', values='Position')
                req_col = results[['Abbreviation', 'TeamColor', 'DriverNumber', 'TeamName', 'GridPosition']].reset_index(drop=True)

                # Reset index of the first table to make Driver a column
                pivot_df_reset = pivot_df.reset_index()

                # Merge with the second table
                new_df = pd.merge(req_col, pivot_df_reset, left_on='Abbreviation', right_on='Driver', how='left')

                new_df = new_df.drop(columns=['Driver'])
                new_df = new_df.sort_values(by='GridPosition', ascending=True)

                import plotly.graph_objects as go

                fig = go.Figure()

                for idx, row in new_df.iterrows():
                    driver = row['Abbreviation']
                    
                    # Get color code safely
                    try:
                        color_str = str(row['TeamColor'])
                        color_str = color_str.split('.')[0] if '.' in color_str else color_str
                        color_code = f"#{color_str}"
                    except (KeyError, AttributeError):
                        color_code = "#FAF5F5"
                    
                    lap_data = row.iloc[4:].values
                    laps = np.arange(1, len(lap_data) + 1)

                    fig.add_trace(
                        go.Scatter(
                            x=laps,
                            y=lap_data,
                            mode='lines',
                            name=driver,
                            line=dict(color=color_code, width=3),
                            hovertemplate=f"<b>{driver}</b><br>Lap: %{{x}}<br>Position: %{{y}}<extra></extra>"
                        )
                    )

                # Layout customization
                fig.update_layout(
                    title=f'F1 {event_name} {year} - {session_type}',
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    font=dict(color='white'),
                    xaxis=dict(title='Lap Number', color='white'),
                    yaxis=dict(title='Race Position', color='white', autorange='reversed'),
                    legend=dict(font=dict(size=10)),
                    height=700,
                    width=1400
                )

                # Optional: Custom tick labels if needed
                fig.update_yaxes(tickvals=list(range(1, 21)), ticktext=new_df['Abbreviation'].tolist())


                st.plotly_chart(fig, use_container_width=True)
            
            
            except Exception as e:
                st.error(f"❌ Failed to load session: {str(e)}")
                st.stop()
    
    elif not event_name:
        st.warning("👈 Now select an event.")
        
elif not year:
    st.warning("👈 Now select a year.")






    


