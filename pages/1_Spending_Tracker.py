import streamlit as st
from helper_functions.auth import require_login, display_user_header, load_user_spending, save_user_spending, add_spending_entry, delete_spending_entry
from helper_functions.spending_tracker import display_spending_tracker

# Page config
st.set_page_config(
    page_title="Spending Tracker",
    page_icon="💳",
    layout="wide"
)

# Check login
if not require_login():
    st.warning("⚠️ Please login from the main page to access this feature.")
    st.stop()
else:
    # Display user info
    display_user_header()
    
    # Get username from session
    username = st.session_state.username
    
    # Display spending tracker
    display_spending_tracker(
        username,
        load_user_spending,
        save_user_spending,
        add_spending_entry,
        delete_spending_entry
    )
