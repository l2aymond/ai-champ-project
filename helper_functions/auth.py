import streamlit as st
import json
import os
from datetime import datetime
from typing import Optional, Dict, List

USER_DATA_FILE = "data/users.json"
SPENDING_DATA_FILE = "data/user_spending.json"
USER_CARDS_FILE = "data/user_cards.json"

def load_users() -> Dict:
    """Load users from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default admin user
        default_users = {
            "admin": {
                "password": "password123",
                "email": "admin@example.com",
                "created_at": datetime.now().isoformat(),
                "role": "admin"
            }
        }
        save_users(default_users)
        return default_users

def save_users(users: Dict):
    """Save users to JSON file"""
    os.makedirs("data", exist_ok=True)
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_user_spending(username: str) -> List[Dict]:
    """Load spending data for a specific user"""
    if os.path.exists(SPENDING_DATA_FILE):
        with open(SPENDING_DATA_FILE, 'r') as f:
            all_spending = json.load(f)
            return all_spending.get(username, [])
    return []

def save_user_spending(username: str, spending_data: List[Dict]):
    """Save spending data for a specific user"""
    os.makedirs("data", exist_ok=True)
    
    # Load all spending data
    if os.path.exists(SPENDING_DATA_FILE):
        with open(SPENDING_DATA_FILE, 'r') as f:
            all_spending = json.load(f)
    else:
        all_spending = {}
    
    # Update user's spending
    all_spending[username] = spending_data
    
    # Save back
    with open(SPENDING_DATA_FILE, 'w') as f:
        json.dump(all_spending, f, indent=2)

def load_user_cards(username: str) -> Dict:
    """Load card settings for a specific user"""
    if os.path.exists(USER_CARDS_FILE):
        with open(USER_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
            return all_cards.get(username, {})
    return {}

def save_user_cards(username: str, cards_data: Dict):
    """Save card settings for a specific user"""
    os.makedirs("data", exist_ok=True)
    
    # Load all cards data
    if os.path.exists(USER_CARDS_FILE):
        with open(USER_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
    else:
        all_cards = {}
    
    # Update user's cards
    all_cards[username] = cards_data
    
    # Save back
    with open(USER_CARDS_FILE, 'w') as f:
        json.dump(all_cards, f, indent=2)

def update_card_settings(username: str, card_name: str, statement_day: int, payment_days: int):
    """Update settings for a specific card"""
    cards_data = load_user_cards(username)
    
    cards_data[card_name] = {
        "statement_day": statement_day,
        "payment_days": payment_days,
        "updated_at": datetime.now().isoformat()
    }
    
    save_user_cards(username, cards_data)

def add_spending_entry(username: str, card_name: str, category: str, amount: float, date: str, notes: str = ""):
    """Add a spending entry for a user"""
    spending_data = load_user_spending(username)
    
    entry = {
        "id": len(spending_data) + 1,
        "card_name": card_name,
        "category": category,
        "amount": amount,
        "date": date,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    spending_data.append(entry)
    save_user_spending(username, spending_data)
    return entry

def delete_spending_entry(username: str, entry_id: int):
    """Delete a spending entry"""
    spending_data = load_user_spending(username)
    spending_data = [entry for entry in spending_data if entry['id'] != entry_id]
    
    # Reindex IDs
    for idx, entry in enumerate(spending_data, 1):
        entry['id'] = idx
    
    save_user_spending(username, spending_data)

def check_login(username: str, password: str) -> bool:
    """Check if username and password are valid"""
    users = load_users()
    return username in users and users[username]['password'] == password

def register_user(username: str, password: str, email: str) -> tuple[bool, str]:
    """Register a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    users[username] = {
        "password": password,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "role": "user"
    }
    
    save_users(users)
    return True, "Registration successful"

def get_user_info(username: str) -> Optional[Dict]:
    """Get user information"""
    users = load_users()
    return users.get(username)

def login_page():
    """Display login/registration page"""
    st.title("🔐 Credit Card Rewards Advisor")
    
    st.markdown("""
    ### Welcome to the Credit Card Rewards Advisor
    This system helps you optimize credit card rewards in Singapore using AI-powered insights.
    Track your spending, discover the best cards, and maximize your rewards!
    """)
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    user_info = get_user_info(username)
                    st.session_state.user_email = user_info.get('email', '')
                    st.session_state.user_role = user_info.get('role', 'user')
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("Choose Username", key="reg_username")
            new_email = st.text_input("Email Address", key="reg_email")
            new_invite_code = st.text_input("Invite Code", key="reg_invite_code")
            new_password = st.text_input("Choose Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            register_submit = st.form_submit_button("Register")
            
            if register_submit:
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    if new_invite_code != "AI_CHAMP_2025":
                        st.error("❌ Invalid invite code")
                    success, message = register_user(new_username, new_password, new_email)
                    if success:
                        st.success(f"✅ {message}! You can now login.")
                    else:
                        st.error(f"❌ {message}")

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.rerun()

def require_login():
    """Check if user is logged in"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    return st.session_state.logged_in

def display_user_header():
    """Display user info in sidebar"""
    if require_login():
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 Logged in as:** {st.session_state.username}")
            if st.session_state.get('user_email'):
                st.markdown(f"**📧 Email:** {st.session_state.user_email}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
            st.markdown("---")
