import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Set page config
st.set_page_config(page_title="Weight Tracker", layout="wide")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'app',
    'password': 'raspberry',
    'database': 'weight_tracker'
}

def init_database():
    """Initialize database and create table if it doesn't exist"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_measurements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                measurement_date DATE NOT NULL,
                weight DECIMAL(5,2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
    except Error as e:
        st.error(f"Database Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    return True

def get_weight_data():
    """Fetch all weight measurements from database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT measurement_date, weight, notes 
            FROM weight_measurements 
            ORDER BY measurement_date DESC
        """)
        
        return cursor.fetchall()
        
    except Error as e:
        st.error(f"Database Error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def add_weight_measurement(date, weight, notes):
    """Add new weight measurement to database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO weight_measurements (measurement_date, weight, notes)
            VALUES (%s, %s, %s)
        """, (date, weight, notes))
        
        conn.commit()
        return True
        
    except Error as e:
        st.error(f"Database Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_latest_weight():
    """Get the most recent weight measurement"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT weight 
            FROM weight_measurements 
            ORDER BY measurement_date DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        return result[0] if result else 70.0
        
    except Error as e:
        st.error(f"Database Error: {e}")
        return 70.0
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def calculate_ema(data, periods=7):
    """Calculate Exponential Moving Average"""
    df = pd.DataFrame(data)
    df['measurement_date'] = pd.to_datetime(df['measurement_date'])
    df = df.sort_values('measurement_date')
    df['ema'] = df['weight'].ewm(span=periods, adjust=False).mean()
    return df

# Initialize database
if not init_database():
    st.error("Failed to initialize database. Please check your database connection.")
    st.stop()

# App title and description
st.title("💪 Weight Tracker")
st.write("Track your weight journey and view trends over time")

# Get the most recent weight for pre-populating the input
default_weight = get_latest_weight()

# Input section
with st.sidebar:
    st.header("Add New Measurement")
    
    # Date input (default to today)
    date = st.date_input("Date", datetime.now())
    
    # Weight input pre-populated with most recent weight
    weight = st.number_input("Weight (kg)", 
                            min_value=20.0, 
                            max_value=300.0, 
                            value=float(default_weight),
                            step=0.1)
    
    # Notes input
    notes = st.text_area("Notes (optional)")
    
    # Submit button
    if st.button("Add Measurement"):
        if add_weight_measurement(date, weight, notes):
            st.success("Measurement added successfully!")
            st.rerun()  # Changed from experimental_rerun() to rerun()

# Get all weight data
weight_data = get_weight_data()

# Main content area
if weight_data:
    # Convert data to DataFrame and calculate EMA
    df = calculate_ema(weight_data)
    
    # Create plot
    fig = go.Figure()
    
    # Add actual weight points
    fig.add_trace(go.Scatter(
        x=df['measurement_date'],
        y=df['weight'],
        mode='markers',
        name='Daily Weight',
        marker=dict(size=8)
    ))
    
    # Add EMA line
    fig.add_trace(go.Scatter(
        x=df['measurement_date'],
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
    df_display = df[['measurement_date', 'weight', 'ema']].copy()
    df_display['measurement_date'] = df_display['measurement_date'].dt.strftime('%Y-%m-%d')
    df_display.columns = ['Date', 'Weight (kg)', '7-Day EMA']
    st.dataframe(df_display.sort_values('Date', ascending=False), hide_index=True)
    
else:
    st.info("No data yet. Add your first weight measurement using the sidebar!")