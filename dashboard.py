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

import streamlit_authenticator as stauth

# --- AUTHENTICATION SETUP ---
# In a real app, you might store this in a yaml file or environment variables
credentials = {
    'usernames': {
        'fudge': {
            'name': 'Fudge',
            'password': '$2b$12$/PoUYqeymevDjfpmuo8S.ertjeVxEj3CmqPcdkWc6RfottJjXR1dK' # Hashed 'izyourboystrap'
        },
        'stu_baby': {
            'name': 'Stu Baby',
            'password': '$2b$12$/PoUYqeymevDjfpmuo8S.ertjeVxEj3CmqPcdkWc6RfottJjXR1dK' # Hashed 'izyourboystrap'
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'baseball_dashboard', # Cookie name
    'abcdef',              # Cookie key (for signing)
    cookie_expiry_days=30  # Persistent for 30 days
)

# Run the login widget (shows "Login" form)
name, authentication_status, username = authenticator.login('main')

if authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()

# authentication_status is True -> Proceed to app
st.sidebar.success(f'Welcome *{name}*')
authenticator.logout('Logout', 'sidebar')

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

tab1, tab2, tab3 = st.tabs(["🏆 Active Matchup", "🆓 Waiver Wire Probables", "🔥 Top Available Pitchers"])

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
    st.header("📋 Probable Starts on Waivers")
    st.markdown("Pitchers starting in the next 7 days who are currently unowned in your league.")
    
    with st.spinner("Scanning MLB scoreboard and checking fantasy ownership..."):
        waiver_data = logic.get_waiver_starts()
        
    if not waiver_data:
        st.info("No unowned probable starters found for the next 7 days.")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Waiver Wire Opportunities")
        with col2:
            st.metric("Total Available", len(waiver_data))
        
        df_waiver = pd.DataFrame(waiver_data)
        st.dataframe(df_waiver, use_container_width=True, hide_index=True)
        st.success(f"Found {len(waiver_data)} available starts!")

with tab3:
    st.header("🔥 Top Unrostered Pitchers")
    st.markdown("Highest percent-owned pitchers currently available (Free Agents or Waivers).")
    
    with st.spinner("Fetching full player pool..."):
        # Increased limit as requested to 100
        top_pitchers = logic.get_top_free_agent_pitchers(limit=100)
        
    if not top_pitchers:
        st.warning("Could not fetch player pool data.")
    else:
        df_top = pd.DataFrame(top_pitchers)
        if not df_top.empty:
            st.dataframe(df_top[["Name", "Owned %", "Position", "Status"]], use_container_width=True, hide_index=True)
            st.info("Showing top 100 pitchers by ownership percentage.")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
