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

with st.spinner("Fetching latest probable starters from ESPN..."):
    data = get_data()

if not data:
    st.error("No current matchup or probable starts found.")
else:
    # Display each team in columns or sequential blocks
    for team_name, starts in data.items():
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header(f"STARTS FOR: {team_name}")
        with col2:
            st.metric("Total Spells", len(starts))
        
        # Convert to DataFrame for a nice Streamlit table
        df = pd.DataFrame(starts)
        
        # Style the table
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
