# Temperature Anomaly Streamlit Dashboard


**Public Link** to view the app:
- https://test-app-zedyd44t5kzx4wbunaetd9.streamlit.app/  

## Quick Start

### 1. Set up your project structure

**Option A: Automated Setup (Recommended)**
```
test-streamlit/
├── app.py
├── requirements.txt
└── data/
    └── GLB.Ts+dSST.csv
```

Create the data directory:
```bash
mkdir data
```
Add GLB.Ts+dSST.csv file into directory

### 2. Install dependencies

```bash
pip install -r requirements.txt
```
### 3. Run the Streamlit app locally
From the project root run the below command

```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

## Features

- 📊 **Interactive Year Range Selection** - Slider controls to explore specific time periods
- 📈 **Smoothing Options** - Apply 5-year or 10-year moving averages to see trends
- 🎯 **Temperature Thresholds** - Visualize +1.5°C and +2.0°C climate targets
- 📉 **Summary Statistics** - Key metrics displayed below the chart
- 📋 **Raw Data Viewer** - Expandable table to view the underlying data

## Data Processing

The app processes the NASA GISTEMP data through these steps:
1. Loads CSV (skipping header row)
2. Strips whitespace from column names
3. Filters to valid 4-digit years
4. Converts Year to integer
5. Converts J-D (annual average) to numeric
6. Drops rows with missing data
7. Filters to years ≥ 1880 (reliable temperature record)
8. Renames J-D column to "Anomaly"
9. Keeps only Year and Anomaly columns

## Data Source

This dashboard uses NASA GISS Surface Temperature Analysis data:
- Website: https://data.giss.nasa.gov/gistemp/
- Direct CSV: https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv

The "J-D" column represents the January-December annual mean temperature anomaly in degrees Celsius relative to the 1951-1980 baseline period.

## Deployment to Streamlit Cloud

1. Create a GitHub repository
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `data/GLB.Ts+dSST.csv` (keep in data folder)
3. Go to https://share.streamlit.io
4. Connect your GitHub repository
5. Select the repository and click "Deploy"

**Note:** Make sure to maintain the `data/` directory structure in your repository!
