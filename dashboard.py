import streamlit as st
import logic
import pandas as pd
from datetime import datetime

# Set page config for a better look
st.set_page_config(
    page_title="Pitching Matchup Tracker",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ Pitching Matchup Tracker")
st.markdown("Track upcoming starts for your team and your current opponent.")

# Add a sidebar for refresh and info
with st.sidebar:
    st.header("Settings")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.info(f"Team ID: {logic.MY_TEAM_ID}\nSeason: {logic.SEASON_ID}")

@st.cache_data(ttl=3600)  # Cache for 1 hour to stay within API limits
def get_data():
    return logic.get_organized_starts()

tab1, tab2 = st.tabs(["🏆 Active Matchup", "🆓 Waiver Wire Probables"])

with tab1:
    with st.spinner("Fetching matchup probables..."):
        data = get_data()

    if not data:
        st.error("No current matchup or probable starts found.")
    else:
        for team_name, starts in data.items():
            st.divider()
            col1, col2 = st.columns([3, 1])
            with col1:
                st.header(f"STARTS FOR: {team_name}")
            with col2:
                st.metric("Total Starts", len(starts))
            
            df = pd.DataFrame(starts)
            st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.header("Available Probable Starters")
    st.markdown("Pitchers starting in the next 7 days who are currently unowned in your league.")
    
    if st.button("🔍 Scan Waiver Wire"):
        with st.spinner("Scanning MLB scoreboard and checking fantasy ownership..."):
            waiver_data = logic.get_waiver_starts()
            
        if not waiver_data:
            st.info("No unowned probable starters found for the next 7 days.")
        else:
            df_waiver = pd.DataFrame(waiver_data)
            st.dataframe(df_waiver, use_container_width=True, hide_index=True)
            st.success(f"Found {len(waiver_data)} available starts!")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
