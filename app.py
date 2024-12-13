import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Set page config
st.set_page_config(page_title="Weight Tracker", layout="wide")

# Initialize session state for data if it doesn't exist
if 'weight_data' not in st.session_state:
    st.session_state.weight_data = []

def calculate_ema(data, periods=7):
    """Calculate Exponential Moving Average"""
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['ema'] = df['weight'].ewm(span=periods, adjust=False).mean()
    return df

def save_data():
    """Save data to a JSON file"""
    with open('weight_data.json', 'w') as f:
        json.dump(st.session_state.weight_data, f)

def load_data():
    """Load data from JSON file if it exists"""
    if os.path.exists('weight_data.json'):
        with open('weight_data.json', 'r') as f:
            st.session_state.weight_data = json.load(f)

# Load existing data
load_data()

# Get the most recent weight for pre-populating the input
default_weight = 70.0  # Default value if no data exists
if st.session_state.weight_data:
    sorted_data = sorted(st.session_state.weight_data, 
                        key=lambda x: x['date'],
                        reverse=True)
    default_weight = sorted_data[0]['weight']

# App title and description
st.title("💪 Weight Tracker")
st.write("Track your weight journey and view trends over time")

# Input section
with st.sidebar:
    st.header("Add New Measurement")
    
    # Date input (default to today)
    date = st.date_input("Date", datetime.now())
    
    # Weight input pre-populated with most recent weight
    weight = st.number_input("Weight (kg)", 
                            min_value=20.0, 
                            max_value=300.0, 
                            value=default_weight,
                            step=0.1)
    
    # Notes input
    notes = st.text_area("Notes (optional)")
    
    # Submit button
    if st.button("Add Measurement"):
        new_entry = {
            "date": date.strftime("%Y-%m-%d"),
            "weight": weight,
            "notes": notes
        }
        st.session_state.weight_data.append(new_entry)
        save_data()
        st.success("Measurement added successfully!")

# Main content area
if st.session_state.weight_data:
    # Convert data to DataFrame and calculate EMA
    df = calculate_ema(st.session_state.weight_data)
    
    # Create plot
    fig = go.Figure()
    
    # Add actual weight points
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['weight'],
        mode='markers',
        name='Daily Weight',
        marker=dict(size=8)
    ))
    
    # Add EMA line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['ema'],
        mode='lines',
        name='7-Day EMA',
        line=dict(width=2, color='red')
    ))
    
    # Update layout
    fig.update_layout(
        title="Weight Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        hovermode='x unified',
        height=500
    )
    
    # Display plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Latest Weight", f"{df['weight'].iloc[-1]:.1f} kg")
    with col2:
        st.metric("Average Weight", f"{df['weight'].mean():.1f} kg")
    with col3:
        total_loss = df['weight'].iloc[-1] - df['weight'].iloc[0]
        st.metric("Total Change", f"{total_loss:.1f} kg")
    with col4:
        st.metric("Days Tracked", len(df))
    
    # Data table
    st.header("History")
    df_display = df[['date', 'weight', 'ema']].copy()
    df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')
    df_display.columns = ['Date', 'Weight (kg)', '7-Day EMA']
    st.dataframe(df_display.sort_values('Date', ascending=False), hide_index=True)
    
else:
    st.info("No data yet. Add your first weight measurement using the sidebar!")