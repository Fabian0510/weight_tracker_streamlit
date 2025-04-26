import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Set page config
st.set_page_config(page_title="Health Tracker", layout="wide")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'app',
    'password': 'raspberry',
    'database': 'weight_tracker'
}

def init_database():
    """Initialize database and create tables if they don't exist"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create weight table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_measurements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                measurement_date DATE NOT NULL,
                weight DECIMAL(5,2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create blood pressure table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_pressure_measurements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                measurement_date DATE NOT NULL,
                systolic INT NOT NULL,
                diastolic INT NOT NULL,
                pulse INT,
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

def get_bp_data():
    """Fetch all blood pressure measurements from database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT measurement_date, systolic, diastolic, pulse, notes 
            FROM blood_pressure_measurements 
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

def add_bp_measurement(date, systolic, diastolic, pulse, notes):
    """Add new blood pressure measurement to database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO blood_pressure_measurements (measurement_date, systolic, diastolic, pulse, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date, systolic, diastolic, pulse, notes))
        
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

def get_latest_bp():
    """Get the most recent blood pressure measurement"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT systolic, diastolic, pulse 
            FROM blood_pressure_measurements 
            ORDER BY measurement_date DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        return result if result else (120, 80, 70)
        
    except Error as e:
        st.error(f"Database Error: {e}")
        return (120, 80, 70)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def calculate_ma(data, value_column, periods=14):
    """Calculate Simple Moving Average"""
    df = pd.DataFrame(data)
    df['measurement_date'] = pd.to_datetime(df['measurement_date'])
    df = df.sort_values('measurement_date')
    df['ma'] = df[value_column].rolling(window=periods, min_periods=1).mean()
    return df

# Initialize database
if not init_database():
    st.error("Failed to initialize database. Please check your database connection.")
    st.stop()

# App title and description
st.title("🩺 Health Tracker")

# Create tabs for data entry
tab1, tab2 = st.tabs(["Weight Tracking", "Blood Pressure Tracking"])

with tab1:
    st.header("Weight Tracker")
    # Get the most recent weight for pre-populating the input
    default_weight = get_latest_weight()

    # Input section
    st.subheader("Add New Weight Measurement")

    # Create three columns for the input fields
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        weight_date = st.date_input("Date", datetime.now(), key="weight_date")

    with col2:
        weight = st.number_input("Weight (kg)", 
                                min_value=20.0, 
                                max_value=300.0, 
                                value=float(default_weight),
                                step=0.1)

    with col3:
        weight_notes = st.text_input("Notes (optional)", key="weight_notes")

    # Center the submit button
    _, center_col, _ = st.columns([3, 1, 3])
    with center_col:
        if st.button("Add Weight Measurement", use_container_width=True):
            if add_weight_measurement(weight_date, weight, weight_notes):
                st.success("Weight measurement added successfully!")
                st.rerun()

with tab2:
    st.header("Blood Pressure Tracker")
    # Get the most recent BP for pre-populating the input
    default_systolic, default_diastolic, default_pulse = get_latest_bp()

    # Input section
    st.subheader("Add New Blood Pressure Measurement")

    # Create columns for the input fields
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        bp_date = st.date_input("Date", datetime.now(), key="bp_date")
        systolic = st.number_input("Systolic (mmHg)", 
                                min_value=70, 
                                max_value=250, 
                                value=int(default_systolic),
                                step=1)

    with col2:
        diastolic = st.number_input("Diastolic (mmHg)", 
                                    min_value=40, 
                                    max_value=150, 
                                    value=int(default_diastolic),
                                    step=1)
        pulse = st.number_input("Pulse (bpm)", 
                                min_value=40, 
                                max_value=200, 
                                value=int(default_pulse),
                                step=1)

    with col3:
        bp_notes = st.text_input("Notes (optional)", key="bp_notes")

    # Center the submit button
    _, center_col, _ = st.columns([3, 1, 3])
    with center_col:
        if st.button("Add BP Measurement", use_container_width=True):
            if add_bp_measurement(bp_date, systolic, diastolic, pulse, bp_notes):
                st.success("Blood pressure measurement added successfully!")
                st.rerun()

# Get data for visualization
weight_data = get_weight_data()
bp_data = get_bp_data()

# Main content area - Combined visualization
st.header("Health Metrics Dashboard")

# Create tabs for visualization
vis_tab1, vis_tab2, vis_tab3 = st.tabs(["Combined View", "Weight Details", "BP Details"])

with vis_tab1:
    if weight_data and bp_data:
        # Process weight data
        weight_df = calculate_ma(weight_data, 'weight')
        
        # Process BP data
        bp_df = pd.DataFrame(bp_data)
        bp_df['measurement_date'] = pd.to_datetime(bp_df['measurement_date'])
        bp_df = bp_df.sort_values('measurement_date')
        bp_df['systolic_ma'] = bp_df['systolic'].rolling(window=14, min_periods=1).mean()
        bp_df['diastolic_ma'] = bp_df['diastolic'].rolling(window=14, min_periods=1).mean()
        
        # Create subplots with 2 y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add weight to primary y-axis
        fig.add_trace(
            go.Scatter(
                x=weight_df['measurement_date'], 
                y=weight_df['weight'],
                mode='markers',
                name='Weight (kg)',
                marker=dict(size=8, opacity=0.4, color='blue'),
                # line=dict(width=1, dash='dot', color='blue')
            ),
            secondary_y=False
        )
        
        # Add weight MA to primary y-axis
        fig.add_trace(
            go.Scatter(
                x=weight_df['measurement_date'], 
                y=weight_df['ma'],
                mode='lines',
                name='Weight 14-Day MA',
                line=dict(width=2, color='darkblue')
            ),
            secondary_y=False
        )
        
        # Add systolic and diastolic to secondary y-axis
        fig.add_trace(
            go.Scatter(
                x=bp_df['measurement_date'], 
                y=bp_df['systolic'],
                mode='markers',
                name='Systolic (mmHg)',
                marker=dict(size=8, opacity=0.4, color='red'),
                # line=dict(width=1, dash='dot', color='red')
            ),
            secondary_y=True
        )
        
        fig.add_trace(
            go.Scatter(
                x=bp_df['measurement_date'], 
                y=bp_df['systolic_ma'],
                mode='lines',
                name='Systolic 14-Day MA',
                line=dict(width=2, color='darkred')
            ),
            secondary_y=True
        )
        
        fig.add_trace(
            go.Scatter(
                x=bp_df['measurement_date'], 
                y=bp_df['diastolic'],
                mode='markers',
                name='Diastolic (mmHg)',
                marker=dict(size=8, opacity=0.4, color='green'),
                # line=dict(width=1, dash='dot', color='green')
            ),
            secondary_y=True
        )
        
        fig.add_trace(
            go.Scatter(
                x=bp_df['measurement_date'], 
                y=bp_df['diastolic_ma'],
                mode='lines',
                name='Diastolic 14-Day MA',
                line=dict(width=2, color='darkgreen')
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title="Combined Health Metrics Over Time",
            hovermode='x unified',
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Weight (kg)", secondary_y=False)
        fig.update_yaxes(title_text="Blood Pressure (mmHg)", secondary_y=True)
        
        # Display plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latest Weight", f"{weight_df['weight'].iloc[-1]:.1f} kg")
        with col2:
            st.metric("Latest BP", f"{bp_df['systolic'].iloc[-1]}/{bp_df['diastolic'].iloc[-1]}")
        with col3:
            weight_change = weight_df['weight'].iloc[-1] - weight_df['weight'].iloc[0]
            st.metric("Weight Change", f"{weight_change:.1f} kg")
        with col4:
            days_tracked = max(len(weight_df), len(bp_df))
            st.metric("Days Tracked", days_tracked)
            
    elif weight_data:
        st.info("Blood pressure data not available yet. Please add your first blood pressure measurement.")
    elif bp_data:
        st.info("Weight data not available yet. Please add your first weight measurement.")
    else:
        st.info("No data yet. Add your first measurements using the forms above!")

with vis_tab2:
    if weight_data:
        # Process data
        df = calculate_ma(weight_data, 'weight')
        
        # Create plot
        fig = go.Figure()
        
        # Add actual weight points with lower opacity
        fig.add_trace(go.Scatter(
            x=df['measurement_date'],
            y=df['weight'],
            mode='markers',
            name='Daily Weight',
            marker=dict(size=8, opacity=0.4),
            # line=dict(width=1, dash='dot')
        ))
        
        # Add MA line
        fig.add_trace(go.Scatter(
            x=df['measurement_date'],
            y=df['ma'],
            mode='lines',
            name='14-Day Moving Average',
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
            st.metric("14-Day MA", f"{df['ma'].iloc[-1]:.1f} kg")
        with col3:
            total_loss = df['weight'].iloc[-1] - df['weight'].iloc[0]
            st.metric("Total Change", f"{total_loss:.1f} kg")
        with col4:
            st.metric("Days Tracked", len(df))
        
        # Data table
        st.header("Weight History")
        df_display = df[['measurement_date', 'weight', 'ma']].copy()
        df_display['measurement_date'] = df_display['measurement_date'].dt.strftime('%Y-%m-%d')
        df_display.columns = ['Date', 'Weight (kg)', '14-Day MA']
        st.dataframe(df_display.sort_values('Date', ascending=False), hide_index=True)
    else:
        st.info("No weight data yet. Add your first weight measurement using the form above!")

with vis_tab3:
    if bp_data:
        # Process data
        bp_df = pd.DataFrame(bp_data)
        bp_df['measurement_date'] = pd.to_datetime(bp_df['measurement_date'])
        bp_df = bp_df.sort_values('measurement_date')
        bp_df['systolic_ma'] = bp_df['systolic'].rolling(window=14, min_periods=1).mean()
        bp_df['diastolic_ma'] = bp_df['diastolic'].rolling(window=14, min_periods=1).mean()
        bp_df['pulse_ma'] = bp_df['pulse'].rolling(window=14, min_periods=1).mean()
        
        # Create plot
        fig = go.Figure()
        
        # Add systolic line
        fig.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['systolic'],
            mode='markers',
            name='Systolic',
            marker=dict(size=8, opacity=0.4, color='red'),
            # line=dict(width=1, dash='dot', color='red')
        ))
        
        # Add systolic MA line
        fig.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['systolic_ma'],
            mode='lines',
            name='Systolic 14-Day MA',
            line=dict(width=2, color='darkred')
        ))
        
        # Add diastolic line
        fig.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['diastolic'],
            mode='markers',
            name='Diastolic',
            marker=dict(size=8, opacity=0.4, color='blue'),
            # line=dict(width=1, dash='dot', color='blue')
        ))
        
        # Add diastolic MA line
        fig.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['diastolic_ma'],
            mode='lines',
            name='Diastolic 14-Day MA',
            line=dict(width=2, color='darkblue')
        ))
        
        # Update layout
        fig.update_layout(
            title="Blood Pressure Trend Over Time",
            xaxis_title="Date",
            yaxis_title="Blood Pressure (mmHg)",
            hovermode='x unified',
            height=500
        )
        
        # Display plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Pulse chart
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['pulse'],
            mode='markers',
            name='Pulse',
            marker=dict(size=8, opacity=0.4, color='green'),
            line=dict(width=1, dash='dot', color='green')
        ))
        
        fig2.add_trace(go.Scatter(
            x=bp_df['measurement_date'],
            y=bp_df['pulse_ma'],
            mode='lines',
            name='Pulse 14-Day MA',
            line=dict(width=2, color='darkgreen')
        ))
        
        # Update layout
        fig2.update_layout(
            title="Pulse Trend Over Time",
            xaxis_title="Date",
            yaxis_title="Pulse (bpm)",
            hovermode='x unified',
            height=300
        )
        
        # Display plot
        st.plotly_chart(fig2, use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_bp = f"{bp_df['systolic'].iloc[-1]}/{bp_df['diastolic'].iloc[-1]}"
            st.metric("Latest BP", latest_bp)
        with col2:
            latest_ma_bp = f"{bp_df['systolic_ma'].iloc[-1]:.1f}/{bp_df['diastolic_ma'].iloc[-1]:.1f}"
            st.metric("14-Day MA", latest_ma_bp)
        with col3:
            st.metric("Latest Pulse", f"{bp_df['pulse'].iloc[-1]} bpm")
        with col4:
            st.metric("Days Tracked", len(bp_df))
        
        # Data table
        st.header("Blood Pressure History")
        bp_display = bp_df[['measurement_date', 'systolic', 'diastolic', 'pulse']].copy()
        bp_display['measurement_date'] = bp_display['measurement_date'].dt.strftime('%Y-%m-%d')
        bp_display.columns = ['Date', 'Systolic', 'Diastolic', 'Pulse']
        st.dataframe(bp_display.sort_values('Date', ascending=False), hide_index=True)
    else:
        st.info("No blood pressure data yet. Add your first BP measurement using the form above!")