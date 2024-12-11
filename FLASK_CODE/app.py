from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import create_engine
import os
from visualizations import create_charts  # Importing the function from visualizations.py
from prediction import predict_crop  # Import the prediction functionality

# Initialize Flask app
app = Flask(__name__)

# SQL Server Database connection details
username = 'INFA_REP'
password = 'INFA_REP'
hostname = 'localhost'
port = '1433'  # Default SQL Server port
database = 'INF_METADATA'

# Build the SQL Server connection string
sqlserver_connection_string = (
    f"mssql+pyodbc://{username}:{password}@{hostname}:{port}/{database}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
)

# Set the SQLALCHEMY_DATABASE_URI configuration
app.config['SQLALCHEMY_DATABASE_URI'] = sqlserver_connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to disable modification tracking

# Create the SQLAlchemy engine and add to app config
engine = create_engine(sqlserver_connection_string)
app.config['SQLALCHEMY_ENGINE'] = engine

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# Fetch data from the selected table (State, Year, or Season)
def fetch_data_from_table(table_name):
    query = f"SELECT * FROM tgt.{table_name}"
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, con=connection)
            pd.options.display.float_format = '{:.0f}'.format  # Format without commas and decimals
            df = df.applymap(lambda x: '{:.0f}'.format(x) if isinstance(x, (int, float)) else x)  # Apply formatting
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Define routes for analysis
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/statewise', methods=['GET', 'POST'])
def statewise():
    if request.method == 'POST':
        state = request.form['state']
        return redirect(url_for('statewise_results', state=state))
    # List of states for the dropdown
    states = [
        "Uttar Pradesh", "Madhya Pradesh", "Karnataka", "Bihar", "Assam",
        "Odisha", "Tamil Nadu", "Maharashtra", "Rajasthan", "Chhattisgarh",
        "Andhra Pradesh", "West Bengal", "Gujarat", "Haryana", "Telangana",
        "Uttarakhand", "Kerala", "Nagaland", "Punjab", "Meghalaya",
        "Arunachal Pradesh", "Himachal Pradesh", "Jammu and Kashmir", "Tripura",
        "Manipur", "Jharkhand", "Mizoram", "Puducherry", "Sikkim",
        "Dadra and Nagar Haveli", "Goa", "Andaman and Nicobar Islands", "Chandigarh"
    ]
    return render_template('statewise.html', states=states)

@app.route('/statewise/<state>')
def statewise_results(state):
    table_name = f"{state.lower().replace(' ', '_')}_crop_production"
    df = fetch_data_from_table(table_name)

    # Image path for the state-specific crop production image
    image_filename = f"{state.lower().replace(' ', '_')}_crop_production.png"
    image_url = url_for('static', filename=f'charts/{image_filename}')
    
    # Check if the image exists in the static/charts directory
    image_path = os.path.join(app.static_folder, 'charts', image_filename)
    if os.path.exists(image_path):
        image_url = url_for('static', filename=f'charts/{image_filename}')
    else:
        image_url = None

    if df is not None:
        df.index = df.index + 1
        return render_template('statewise.html', table=df.to_html(classes="table table-striped"), state=state, image_url=image_url)
    
    return render_template('statewise.html', error=f"Error fetching data for {state}")

@app.route('/yearwise', methods=['GET', 'POST'])
def yearwise():
    if request.method == 'POST':
        year = request.form['year']
        return redirect(url_for('yearwise_results', year=year))
    return render_template('yearwise.html', years=[str(y) for y in range(1997, 2016)])

@app.route('/yearwise/<year>')
def yearwise_results(year):
    table_name = f"crop_production_{year}"
    df = fetch_data_from_table(table_name)
    
    # Image path for the year-specific crop production image
    image_filename = f"{year}_statewise_crop_production.png"
    image_url = url_for('static', filename=f'charts/{image_filename}')
    
    # Check if the image exists in the static/charts directory
    image_path = os.path.join(app.static_folder, 'charts', image_filename)
    if os.path.exists(image_path):
        image_url = url_for('static', filename=f'charts/{image_filename}')
    else:
        image_url = None

    if df is not None:
        df.index = df.index + 1
        return render_template('yearwise.html', table=df.to_html(classes="table table-striped"), year=year, image_url=image_url)
    
    return render_template('yearwise.html', error=f"Error fetching data for {year}")

@app.route('/seasonwise', methods=['GET', 'POST'])
def seasonwise():
    if request.method == 'POST':
        season = request.form['season']
        return redirect(url_for('seasonwise_results', season=season))
    return render_template('seasonwise.html', seasons=["Whole Year", "Rabi", "Kharif", "Autumn", "Winter", "Summer"])

@app.route('/seasonwise/<season>')
def seasonwise_results(season):
    # Create the table name dynamically based on the season
    table_name = f"{season.lower().replace(' ', '_')}_crop_production"
    df = fetch_data_from_table(table_name)
    
    # Construct the filename for the season-specific crop production image
    image_filename = f"{season.lower().replace(' ', '_')}_most_produced_crops.png"
    
    # Construct the image URL and check if the file exists in the static/charts directory
    image_path = os.path.join(app.static_folder, 'charts', image_filename)
    
    if os.path.exists(image_path):
        image_url = url_for('static', filename=f'charts/{image_filename}')
    else:
        image_url = None

    if df is not None:
        df.index = df.index + 1  # Adjust index for display
        return render_template('seasonwise.html', 
                               table=df.to_html(classes="table table-striped"), 
                               season=season, 
                               image_url=image_url)
    
    return render_template('seasonwise.html', error=f"Error fetching data for {season}")

# Visualizations route
@app.route('/visualizations')
def visualizations():
    charts = create_charts()  # No need to pass the app instance now
    return render_template('visualizations.html', charts=charts)

# Prediction route for crop and weather
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        state = request.form['state']
        district = request.form['district']
        year = int(request.form['year'])
        season = request.form['season']
        area = float(request.form['area'])
        city_name = request.form['city_name']  # Get the city for weather data
        
        # Call the prediction function from prediction.py
        crop, weather_info = predict_crop(state, district, year, season, area, city_name)

        if isinstance(crop, str) and 'Error' in crop:
            return render_template('prediction.html', error=f"Error: {crop}")
        
        return render_template('result.html', crop=crop, weather_info=weather_info)
    
    return render_template('prediction.html')

if __name__ == '__main__':
    app.run(debug=True)
