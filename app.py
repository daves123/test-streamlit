import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Temperature Anomaly Dashboard",
    page_icon="🌡️",
    layout="wide"
)

# Title and description
st.title("🌡️ Interactive Temperature Anomaly Dashboard")
st.markdown("Explore global temperature anomalies with interactive controls for year range, smoothing, and threshold visualization.")

# Load data
@st.cache_data
def load_data():
    """Load and cache the temperature data - matches NASA GISTEMP processing"""
    # Load CSV from data directory, skipping the header row
    df = pd.read_csv('data/GLB.Ts+dSST.csv', skiprows=1)
    
    # Strip whitespace from column names
    df = df.rename(columns=lambda c: c.strip())
    
    # Filter to valid 4-digit years only
    df = df[df["Year"].astype(str).str.match(r"^\d{4}$", na=False)]
    
    # Convert Year to integer
    df["Year"] = df["Year"].astype(int)
    
    # Convert J-D (January-December annual average) to numeric
    df["J-D"] = pd.to_numeric(df["J-D"], errors="coerce")
    
    # Drop rows with missing J-D values
    df = df.dropna(subset=["J-D"]).copy()
    
    # Filter to years >= 1880 (reliable temperature record starts here)
    df = df[df["Year"] >= 1880]
    
    # Rename J-D to Anomaly for clarity
    df = df.rename(columns={"J-D": "Anomaly"})
    
    # Keep only Year and Anomaly columns
    df = df[["Year", "Anomaly"]].reset_index(drop=True)
    
    return df

try:
    df = load_data()
    
    # Debug: Show available columns
    st.sidebar.info(f"Data loaded: {len(df)} rows")
    
    # Get year range from data
    years = sorted(df['Year'].unique().tolist())
    y_min, y_max = int(years[0]), int(years[-1])
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Year range sliders
    st.sidebar.subheader("Year Range")
    start_year = st.sidebar.slider(
        "Start Year",
        min_value=y_min,
        max_value=y_max,
        value=y_min,
        step=1
    )
    
    end_year = st.sidebar.slider(
        "End Year",
        min_value=y_min,
        max_value=y_max,
        value=y_max,
        step=1
    )
    
    # Smoothing option
    st.sidebar.subheader("Smoothing")
    smooth_option = st.sidebar.selectbox(
        "Smoothing Window",
        options=["None", "5-year", "10-year"],
        index=2
    )
    
    # Map smoothing option to window size
    smooth_map = {"None": 0, "5-year": 5, "10-year": 10}
    smooth_k = smooth_map[smooth_option]
    
    # Threshold option
    st.sidebar.subheader("Threshold")
    threshold_option = st.sidebar.selectbox(
        "Temperature Threshold",
        options=["None", "+1.5°C", "+2.0°C"],
        index=1
    )
    
    # Map threshold option to value
    threshold_map = {"None": None, "+1.5°C": 1.5, "+2.0°C": 2.0}
    thresh = threshold_map[threshold_option]
    
    # Validate and fix year range
    if start_year > end_year:
        start_year, end_year = end_year, start_year
        st.warning("Start year was greater than end year. Years have been swapped.")
    
    # Filter data by year range
    d = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)].copy()
    
    if d.empty:
        st.error(f"No data available between {start_year} and {end_year}.")
    else:
        # Apply smoothing
        if smooth_k and smooth_k > 1:
            d['Smoothed'] = d['Anomaly'].rolling(
                window=int(smooth_k),
                center=True,
                min_periods=1
            ).mean()
        else:
            d['Smoothed'] = np.nan
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add annual anomaly trace
        fig.add_trace(go.Scatter(
            x=d['Year'],
            y=d['Anomaly'],
            mode='lines',
            name='Annual',
            line=dict(color="firebrick", width=2)
        ))
        
        # Add smoothed trace if applicable
        if d['Smoothed'].notna().any():
            fig.add_trace(go.Scatter(
                x=d['Year'],
                y=d['Smoothed'],
                mode='lines',
                name=f'{smooth_k}-year smooth',
                line=dict(color="black", width=3)
            ))
        
        # Add baseline at 0
        fig.add_hline(y=0, line_dash='dash', line_color='gray')
        
        # Add threshold line if specified
        if thresh is not None:
            fig.add_hline(
                y=float(thresh),
                line_dash='dot',
                line_color='orange',
                annotation_text=f"{thresh}°C threshold"
            )
        
        # Annotate latest year
        last_row = d.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_row['Year']],
            y=[last_row['Anomaly']],
            mode='markers+text',
            marker=dict(size=10, color='red'),
            text=[f"{last_row['Anomaly']:.2f}°C"],
            textposition="top center",
            name="Latest year",
            showlegend=True
        ))
        
        # Update layout
        fig.update_layout(
            title="Global Temperature Anomaly — Explore Years, Smoothing, and Thresholds",
            xaxis_title="Year",
            yaxis_title="Temperature Anomaly (°C)",
            template="plotly_white",
            height=550,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Latest Anomaly",
                f"{last_row['Anomaly']:.2f}°C",
                delta=f"{last_row['Anomaly'] - d.iloc[0]['Anomaly']:.2f}°C since {start_year}"
            )
        
        with col2:
            st.metric(
                "Average Anomaly",
                f"{d['Anomaly'].mean():.2f}°C"
            )
        
        with col3:
            st.metric(
                "Maximum Anomaly",
                f"{d['Anomaly'].max():.2f}°C",
                delta=f"Year {d.loc[d['Anomaly'].idxmax(), 'Year']:.0f}"
            )
        
        with col4:
            st.metric(
                "Data Points",
                f"{len(d)}"
            )
        
        # Optional: Show data table
        with st.expander("View Raw Data"):
            st.dataframe(d[['Year', 'Anomaly', 'Smoothed']].tail(20))

except FileNotFoundError:
    st.error("❌ Data file 'data/GLB.Ts+dSST.csv' not found. Please ensure the file is in the data/ directory")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown("*Dashboard created with Streamlit • Data: Global Temperature Anomalies*")