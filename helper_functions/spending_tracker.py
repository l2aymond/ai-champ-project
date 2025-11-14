import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import plotly.express as px
import plotly.graph_objects as go

# Singapore credit card categories
SPENDING_CATEGORIES = [
    "Online Shopping",
    "Dining",
    "Groceries",
    "Travel",
    "Transport",
    "Entertainment",
    "Fuel",
    "Bills & Utilities",
    "Foreign Currency",
    "Shopping (Retail)",
    "Others"
]

# Common Singapore credit cards
CREDIT_CARDS = [
    "DBS Woman's World Card",
    "Citi Rewards Mastercard",
    "Maybank XL Rewards",
    "HSBC Revolution",
    "UOB Lady's Solitaire",
    "UOB Preferred Platinum Visa",
    "UOB Visa Signature",
    "KrisFlyer UOB Credit Card",
    "AMEX KrisFlyer Ascend",
    "DBS Altitude",
    "Standard Chartered Journey",
    "Citi PremierMiles",
    "UOB PRVI Miles",
    "AMEX HighFlyer",
    "Maybank Horizon Visa Signature",
    "Other"
]

def display_spending_tracker(username: str, load_user_spending, save_user_spending, add_spending_entry, delete_spending_entry):
    """Display spending tracker interface"""
    st.header("💳 Credit Card Spending Tracker")
    
    st.markdown("""
    Track your credit card spending to understand your patterns and optimize your rewards.
    """)
    
    # Load user's spending data
    spending_data = load_user_spending(username)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Spending", "📝 Manage Entries"])
    
    with tab1:
        display_spending_dashboard(spending_data)
    
    with tab2:
        display_add_spending_form(username, add_spending_entry)
    
    with tab3:
        display_manage_entries(username, spending_data, delete_spending_entry)

def display_spending_dashboard(spending_data: List[Dict]):
    """Display spending analytics dashboard"""
    if not spending_data:
        st.info("📊 No spending data yet. Add your first transaction in the 'Add Spending' tab!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(spending_data)
    df['amount'] = pd.to_numeric(df['amount'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spending = df['amount'].sum()
        st.metric("Total Spending", f"S${total_spending:,.2f}")
    
    with col2:
        avg_transaction = df['amount'].mean()
        st.metric("Avg Transaction", f"S${avg_transaction:,.2f}")
    
    with col3:
        num_transactions = len(df)
        st.metric("Total Transactions", num_transactions)
    
    with col4:
        num_cards = df['card_name'].nunique()
        st.metric("Cards Used", num_cards)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spending by Category")
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        fig_category = px.pie(
            values=category_spending.values,
            names=category_spending.index,
            title="",
            hole=0.4
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("Spending by Card")
        card_spending = df.groupby('card_name')['amount'].sum().sort_values(ascending=False)
        fig_card = px.bar(
            x=card_spending.values,
            y=card_spending.index,
            orientation='h',
            title="",
            labels={'x': 'Amount (S$)', 'y': 'Card'}
        )
        st.plotly_chart(fig_card, use_container_width=True)
    
    # Time series
    st.subheader("Spending Over Time")
    daily_spending = df.groupby('date')['amount'].sum().reset_index()
    fig_time = px.line(
        daily_spending,
        x='date',
        y='amount',
        title="",
        labels={'date': 'Date', 'amount': 'Amount (S$)'}
    )
    fig_time.update_traces(mode='lines+markers')
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Category breakdown by card
    st.subheader("Category Breakdown by Card")
    pivot_data = df.pivot_table(
        values='amount',
        index='card_name',
        columns='category',
        aggfunc='sum',
        fill_value=0
    )
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Blues',
        text=pivot_data.values.round(2),
        texttemplate='S$%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    fig_heatmap.update_layout(
        title="",
        xaxis_title="Category",
        yaxis_title="Card",
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Recent transactions
    st.subheader("Recent Transactions")
    recent_df = df.sort_values('date', ascending=False).head(10)
    display_df = recent_df[['date', 'card_name', 'category', 'amount', 'notes']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"S${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def display_add_spending_form(username: str, add_spending_entry):
    """Display form to add new spending entry"""
    st.subheader("Add New Spending Entry")
    
    with st.form("add_spending_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            card_name = st.selectbox("Credit Card", CREDIT_CARDS)
            if card_name == "Other":
                card_name = st.text_input("Enter Card Name")
            
            category = st.selectbox("Category", SPENDING_CATEGORIES)
        
        with col2:
            amount = st.number_input("Amount (S$)", min_value=0.01, step=0.01, format="%.2f")
            date = st.date_input("Date", value=datetime.now())
        
        notes = st.text_area("Notes (Optional)", placeholder="e.g., Lunch at Marina Bay, Grab ride to office")
        
        submit = st.form_submit_button("Add Entry", use_container_width=True, type="primary")
        
        if submit:
            if not card_name:
                st.error("Please enter a card name")
            else:
                entry = add_spending_entry(
                    username=username,
                    card_name=card_name,
                    category=category,
                    amount=amount,
                    date=date.strftime('%Y-%m-%d'),
                    notes=notes
                )
                st.success(f"✅ Added spending entry: S${amount:.2f} on {card_name}")
                st.rerun()

def display_manage_entries(username: str, spending_data: List[Dict], delete_spending_entry):
    """Display interface to manage existing entries"""
    st.subheader("Manage Spending Entries")
    
    if not spending_data:
        st.info("No spending entries to manage.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(spending_data)
    df['amount'] = df['amount'].apply(lambda x: f"S${float(x):,.2f}")
    
    # Display with delete option
    st.dataframe(df[['id', 'date', 'card_name', 'category', 'amount', 'notes']], use_container_width=True, hide_index=True)
    
    # Delete entry
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        entry_id = st.number_input("Enter Entry ID to Delete", min_value=1, max_value=len(spending_data), step=1)
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Delete Entry", type="primary"):
            delete_spending_entry(username, entry_id)
            st.success(f"✅ Deleted entry #{entry_id}")
            st.rerun()
    
    # Export option
    st.markdown("---")
    st.subheader("Export Data")
    
    if st.button("📥 Download as CSV"):
        csv = pd.DataFrame(spending_data).to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"spending_data_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
