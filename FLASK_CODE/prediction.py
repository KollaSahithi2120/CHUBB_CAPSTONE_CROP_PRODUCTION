import joblib
import requests
import numpy as np

# Load the trained model and label encoders
model = joblib.load('crop_model_rf.pkl')
le_state = joblib.load('label_encoder_state.pkl')
le_district = joblib.load('label_encoder_district.pkl')
le_season = joblib.load('label_encoder_season.pkl')
le_crop = joblib.load('label_encoder_crop.pkl')

# OpenWeatherMap API key (replace with your own API key)
API_KEY = 'your_openweathermap_api_key'

# Function to fetch weather data from OpenWeatherMap API
def get_weather_data(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return "Weather data not available"
    
    # Extract the necessary weather details
    weather_data = {
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'weather': data['weather'][0]['description']
    }
    return weather_data

# Function to predict the crop based on input data
def predict_crop(state, district, year, season, area, city_name):
    try:
        # Encode input data
        state_code = le_state.transform([state])[0]
        district_code = le_district.transform([district])[0]
        season_code = le_season.transform([season])[0]

        # Prepare features for prediction
        features = np.array([[state_code, district_code, year, season_code, area]])

        # Make the prediction
        crop_code = model.predict(features)[0]
        crop_name = le_crop.inverse_transform([crop_code])[0]

        # Fetch weather data for the given city (district in this case)
        weather_data = get_weather_data(city_name)

        return crop_name, weather_data

    except Exception as e:
        return f"Error in prediction: {e}", None
