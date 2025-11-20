import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import plotly.express as px
import plotly.graph_objects as go
import json
import os

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

def get_statement_period(transaction_date: datetime, statement_day: int) -> tuple[datetime, datetime]:
    """Calculate the statement period for a given transaction date"""
    # If transaction is on or before statement day, it belongs to period ending in this month
    # e.g. Statement day 15. Trans date Nov 10. Period: Oct 16 - Nov 15.
    # e.g. Statement day 15. Trans date Nov 20. Period: Nov 16 - Dec 15.
    
    if transaction_date.day <= statement_day:
        end_date = transaction_date.replace(day=statement_day)
        start_date = (end_date - timedelta(days=1)).replace(day=statement_day) + timedelta(days=1)
        # Handle month rollover for start date
        if start_date.month == end_date.month:
            # This happens if we just subtracted days, but we need to go back a month
            # Actually easier logic:
            # End date is this month's statement day
            # Start date is previous month's statement day + 1
            pass
            
    # Let's refine logic
    # If trans_date <= statement_day:
    #   Period End = Year-Month-StatementDay
    #   Period Start = (Period End - 1 month) + 1 day
    # Else:
    #   Period End = (Year-Month-StatementDay) + 1 month
    #   Period Start = Year-Month-StatementDay + 1 day
    
    if transaction_date.day <= statement_day:
        period_end = transaction_date.replace(day=statement_day)
        # Go back one month for start
        if period_end.month == 1:
            period_start = period_end.replace(year=period_end.year-1, month=12) + timedelta(days=1)
        else:
            # Handle edge cases where prev month has fewer days? 
            # Actually, statement day is fixed. If prev month doesn't have that day... 
            # Let's assume valid dates for now or clamp.
            # Better: period_end - 1 month is tricky.
            # Let's use dateutil or simple logic
            first_of_month = period_end.replace(day=1)
            last_of_prev_month = first_of_month - timedelta(days=1)
            # This is getting complicated with day 31.
            # Simplified assumption: Statement day is valid for all months or clamped.
            # For now, let's just use simple logic and rely on datetime to handle it if possible, 
            # but datetime.replace fails for invalid days.
            
            # Robust way:
            # Period End is definitely in the current month (since day <= statement_day)
            # Start is previous month.
            prev_month = period_end.month - 1
            prev_year = period_end.year
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
            
            # Handle invalid days (e.g. statement day 31, prev month Feb)
            # We will clamp to max days in month
            import calendar
            _, max_days = calendar.monthrange(prev_year, prev_month)
            start_day = min(statement_day, max_days)
            
            period_start = datetime(prev_year, prev_month, start_day) + timedelta(days=1)
            
    else:
        # Transaction after statement day
        # Period Start = This month statement day + 1
        # Period End = Next month statement day
        
        period_start = transaction_date.replace(day=statement_day) + timedelta(days=1)
        
        next_month = transaction_date.month + 1
        next_year = transaction_date.year
        if next_month == 13:
            next_month = 1
            next_year += 1
            
        import calendar
        _, max_days = calendar.monthrange(next_year, next_month)
        end_day = min(statement_day, max_days)
        
        period_end = datetime(next_year, next_month, end_day)

    return period_start, period_end

def load_card_rules() -> Dict:
    """Load card rules from JSON file"""
    try:
        file_path = os.path.join("data", "card_rules.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading card rules: {e}")
    return {}

def calculate_optimization_status(spending_df: pd.DataFrame, card_rules: Dict, selected_period_df: pd.DataFrame) -> Dict:
    """
    Calculate optimization status for each card based on rules and current spending.
    Returns a dictionary with card status.
    """
    status = {}
    
    if spending_df.empty:
        return status
        
    # We need to filter spending based on the relevant period for optimization.
    # Typically this is the current month or statement month.
    # For simplicity in this view, we will use the 'selected_period_df' passed from dashboard
    # which is already filtered by the user's selection (e.g. "Oct 16 - Nov 15").
    
    # Group by Card and Category
    spending_by_card_cat = selected_period_df.groupby(['card_name', 'category'])['amount'].sum().to_dict()
    total_spending_by_card = selected_period_df.groupby('card_name')['amount'].sum().to_dict()
    
    for card_name, rules in card_rules.items():
        # Check if user has this card in their spending
        # (We might want to show cards even if 0 spend, but for now let's show active ones 
        # or ones in the user's wallet if we had that list. We'll stick to active spend + rules keys)
        
        card_status = {
            "caps": [],
            "min_spend": None
        }
        
        # 1. Check Caps
        if "caps" in rules:
            for cap in rules["caps"]:
                # Determine relevant categories (primary + shared)
                categories = [cap["category"]]
                if "shared_with" in cap:
                    categories.extend(cap["shared_with"])
                
                # Calculate total spend for these categories
                current_spend = 0
                for cat in categories:
                    current_spend += spending_by_card_cat.get((card_name, cat), 0)
                
                limit = cap["amount"]
                percent = min(current_spend / limit, 1.0) * 100 if limit > 0 else 0
                is_exceeded = current_spend > limit
                
                card_status["caps"].append({
                    "description": cap["description"],
                    "current": current_spend,
                    "limit": limit,
                    "percent": percent,
                    "is_exceeded": is_exceeded,
                    "remaining": max(limit - current_spend, 0)
                })
        
        # 2. Check Min Spend
        if "min_spend" in rules and rules["min_spend"] > 0:
            min_spend = rules["min_spend"]
            # Special logic for UOB Visa Sig (per category min spend) - simplified for now to total
            # The rule file says "min_spend_scope": "per_category" for VS, but let's handle general case first
            
            current_total = total_spending_by_card.get(card_name, 0)
            
            is_met = current_total >= min_spend
            percent = min(current_total / min_spend, 1.0) * 100
            
            card_status["min_spend"] = {
                "amount": min_spend,
                "current": current_total,
                "percent": percent,
                "is_met": is_met,
                "shortfall": max(min_spend - current_total, 0)
            }
            
        if card_status["caps"] or card_status["min_spend"]:
            status[card_name] = card_status
            
    return status

def display_spending_tracker(username: str, load_user_spending, save_user_spending, add_spending_entry, delete_spending_entry, load_user_cards, update_card_settings):
    """Display spending tracker interface"""
    st.header("💳 Credit Card Spending Tracker")
    
    st.markdown("""
    Track your credit card spending to understand your patterns and optimize your rewards.
    """)
    
    # Load user's spending data
    spending_data = load_user_spending(username)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Spending", "📝 Manage Entries", "⚙️ Card Settings"])
    
    with tab1:
        display_spending_dashboard(spending_data, username, load_user_cards)
    
    with tab2:
        display_add_spending_form(username, add_spending_entry)
    
    with tab3:
        display_manage_entries(username, spending_data, delete_spending_entry)

    with tab4:
        display_card_settings(username, load_user_cards, update_card_settings)

def display_spending_dashboard(spending_data: List[Dict], username: str, load_user_cards):
    """Display spending analytics dashboard"""
    if not spending_data:
        st.info("📊 No spending data yet. Add your first transaction in the 'Add Spending' tab!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(spending_data)
    df['amount'] = pd.to_numeric(df['amount'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Load card settings
    user_cards = load_user_cards(username)
    
    # Calculate statement periods for each transaction
    def assign_period(row):
        card_settings = user_cards.get(row['card_name'], {})
        statement_day = card_settings.get('statement_day')
        
        if statement_day:
            start, end = get_statement_period(row['date'], statement_day)
            return f"{start.strftime('%d %b')} - {end.strftime('%d %b %Y')}", end
        return "Unassigned", pd.NaT

    # Apply period calculation
    if user_cards:
        period_results = df.apply(assign_period, axis=1, result_type='expand')
        df['statement_period'] = period_results[0]
        df['statement_end_date'] = period_results[1]
    else:
        df['statement_period'] = "All Time"
        df['statement_end_date'] = pd.NaT

    # Filter by Statement Period
    st.subheader("📅 Statement Period View")
    
    # Get unique periods sorted by date
    if user_cards:
        unique_periods = df[df['statement_period'] != "Unassigned"].sort_values('statement_end_date', ascending=False)['statement_period'].unique()
        unique_periods = ["Unsettled Statement Period"] + list(unique_periods) + ["Unassigned", "All Time"]
    else:
        unique_periods = ["All Time"]
        
    selected_period = st.selectbox("Select Statement Period", unique_periods)
    
    # Filter data
    if selected_period == "Unsettled Statement Period":
        # Filter for transactions in the current active statement period for each card
        # Normalize to midnight to avoid time comparison issues
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        def is_in_current_period(row):
            card_settings = user_cards.get(row['card_name'], {})
            statement_day = card_settings.get('statement_day')
            
            if statement_day:
                # Get the period that TODAY falls into
                cur_start, cur_end = get_statement_period(current_date, statement_day)
                # Check if transaction date is within this period
                return cur_start <= row['date'] <= cur_end
            return False
            
        filtered_df = df[df.apply(is_in_current_period, axis=1)].copy()
        
        if filtered_df.empty:
             st.info(f"No transactions found for the current statement period (as of {current_date.strftime('%d %b')}).")
             return

    elif selected_period != "All Time":
        filtered_df = df[df['statement_period'] == selected_period].copy()
    else:
        filtered_df = df.copy()
        
    if filtered_df.empty:
        st.info("No transactions for this period.")
        return

    # Calculate Payment Due Date if specific period selected
    payment_due_msg = ""
    if selected_period not in ["All Time", "Unassigned"] and not filtered_df.empty:
        # Get the statement end date for this period (from first row)
        stmt_end = filtered_df.iloc[0]['statement_end_date']
        
        # We need to check if multiple cards are mixed in this view.
        # Usually statement periods are card-specific, but if we filter by a text string like "16 Oct - 15 Nov",
        # it might group multiple cards if they happen to have same statement day.
        # But payment due date depends on card.
        
        # Let's show breakdown by card for payment dates
        cards_in_period = filtered_df['card_name'].unique()
        due_dates = []
        
        for card in cards_in_period:
            settings = user_cards.get(card, {})
            payment_days = settings.get('payment_days', 20) # Default 20 days
            if pd.notna(stmt_end):
                due_date = stmt_end + timedelta(days=payment_days)
                due_dates.append(f"**{card}**: {due_date.strftime('%d %b %Y')}")
        
        if due_dates:
            payment_due_msg = " | ".join(due_dates)

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spending = filtered_df['amount'].sum()
        st.metric("Total Spending", f"S${total_spending:,.2f}")
    
    with col2:
        avg_transaction = filtered_df['amount'].mean()
        st.metric("Avg Transaction", f"S${avg_transaction:,.2f}")
    
    with col3:
        num_transactions = len(filtered_df)
        st.metric("Transactions", num_transactions)
    
    with col4:
        if payment_due_msg:
            st.markdown(f"**Est. Payment Due:**\n\n{payment_due_msg}")
        else:
            num_cards = filtered_df['card_name'].nunique()
            st.metric("Cards Used", num_cards)
    
    st.markdown("---")
    
    # --- Optimization Tracker Section ---
    st.subheader("🎯 Optimization Tracker")
    
    # Load rules
    card_rules = load_card_rules()
    
    # Calculate status
    opt_status = calculate_optimization_status(df, card_rules, filtered_df)
    
    if not opt_status:
        st.info("No optimization rules found for your active cards in this period.")
    else:
        # Display status for each card
        for card_name, status in opt_status.items():
            # Only show if card is present in filtered_df (active in this period)
            if card_name in filtered_df['card_name'].unique():
                with st.expander(f"**{card_name}**", expanded=True):
                    # Caps
                    if status["caps"]:
                        st.markdown("###### Bonus Caps")
                        for cap in status["caps"]:
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.progress(cap["percent"] / 100, text=f"{cap['description']}")
                            with col_b:
                                color = "red" if cap["is_exceeded"] else "green"
                                st.markdown(f":{color}[**S${cap['current']:,.2f} / S${cap['limit']:,.0f}**]")
                                if cap["is_exceeded"]:
                                    st.caption(f"Exceeded by S${cap['current'] - cap['limit']:,.2f}")
                                else:
                                    st.caption(f"Remaining: S${cap['remaining']:,.2f}")
                    
                    # Min Spend
                    if status["min_spend"]:
                        st.markdown("###### Minimum Spend Requirement")
                        ms = status["min_spend"]
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.progress(ms["percent"] / 100, text=f"Min Spend S${ms['amount']}")
                        with col_b:
                            color = "green" if ms["is_met"] else "orange"
                            st.markdown(f":{color}[**S${ms['current']:,.2f} / S${ms['amount']:,.0f}**]")
                            if not ms["is_met"]:
                                st.caption(f"Shortfall: S${ms['shortfall']:,.2f}")
                            else:
                                st.caption("✅ Requirement Met")

    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Spending by Category")
        category_spending = filtered_df.groupby('category')['amount'].sum().sort_values(ascending=False)
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
        card_spending = filtered_df.groupby('card_name')['amount'].sum().sort_values(ascending=False)
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
    daily_spending = filtered_df.groupby('date')['amount'].sum().reset_index()
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
    pivot_data = filtered_df.pivot_table(
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
    st.subheader("Transactions in Period")
    recent_df = filtered_df.sort_values('date', ascending=False)
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
    
    csv = pd.DataFrame(spending_data).to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"spending_data_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def display_card_settings(username: str, load_user_cards, update_card_settings):
    """Display interface to manage card settings"""
    st.subheader("⚙️ Card Settings")
    st.markdown("Configure statement dates and payment timeframes for your credit cards.")
    
    # Load current settings
    user_cards = load_user_cards(username)
    
    # Select card to configure
    card_name = st.selectbox("Select Card to Configure", CREDIT_CARDS)
    if card_name == "Other":
        card_name = st.text_input("Enter Card Name for Settings")
    
    if card_name:
        current_settings = user_cards.get(card_name, {})
        
        with st.form(f"settings_form_{card_name}"):
            st.markdown(f"**Settings for {card_name}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                statement_day = st.number_input(
                    "Statement Day (1-31)", 
                    min_value=1, 
                    max_value=31, 
                    value=current_settings.get('statement_day', 1),
                    help="The day of the month when your statement is generated."
                )
            
            with col2:
                payment_days = st.number_input(
                    "Payment Due Days", 
                    min_value=1, 
                    max_value=60, 
                    value=current_settings.get('payment_days', 20),
                    help="Number of days after statement date until payment is due."
                )
            
            submit = st.form_submit_button("Save Settings", type="primary")
            
            if submit:
                update_card_settings(username, card_name, statement_day, payment_days)
                st.success(f"✅ Settings saved for {card_name}")
                st.rerun()
    
    # Display current configuration summary
    if user_cards:
        st.markdown("---")
        st.subheader("Current Configurations")
        
        config_data = []
        for card, settings in user_cards.items():
            config_data.append({
                "Card": card,
                "Statement Day": settings.get('statement_day'),
                "Payment Due (Days)": settings.get('payment_days'),
                "Last Updated": settings.get('updated_at', '').split('T')[0]
            })
        
        st.dataframe(pd.DataFrame(config_data), use_container_width=True, hide_index=True)
