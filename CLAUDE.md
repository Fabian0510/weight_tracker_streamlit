# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Streamlit-based health tracker application that allows users to:
- Track weight measurements
- Track blood pressure measurements (systolic, diastolic, and pulse)
- Visualize health data with interactive charts
- View historical data in tabular format

The application uses:
- Streamlit for the web interface
- Plotly for interactive data visualization
- MySQL database for data storage
- Pandas for data manipulation

## Running the Application

To run the application locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

## Database Setup

The application requires a MySQL database with the following configuration:
- Host: localhost
- User: app
- Password: raspberry
- Database: weight_tracker

The application will automatically create the necessary tables when it starts.

## Code Structure

- `app.py`: Main application file containing all the code
  - Database functions (init_database, get_weight_data, etc.)
  - UI components (tabs, forms, charts)
  - Data processing and visualization logic

- `weight_data.json`: Sample weight data (may be used as a fallback or for testing)

## Key Components

1. **Database Functions**:
   - `init_database()`: Creates the necessary database tables if they don't exist
   - `get_weight_data()`, `get_bp_data()`: Retrieve measurements from the database
   - `add_weight_measurement()`, `add_bp_measurement()`: Add new measurements
   - `get_latest_weight()`, `get_latest_bp()`: Get the most recent measurements

2. **Data Processing**:
   - `calculate_ma()`: Calculate moving averages for smoothing time series data

3. **UI Components**:
   - Tabs for weight and blood pressure tracking
   - Forms for adding new measurements
   - Interactive charts for visualizing trends
   - Statistics and data tables

## Development Notes

When working on this application:
- Remember to handle database connections properly (opening/closing)
- Use try/except blocks for database operations to handle potential errors
- Consider the mobile view, as Streamlit apps can be accessed from various devices