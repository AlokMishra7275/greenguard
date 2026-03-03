import requests
import csv
import time
from datetime import datetime

API_KEY = "89f62a1db71b83cf3425daa1cfb9a2d5"   # keep your AQI API key

# Multiple cities (lat, lon)
CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
}

CSV_FILE = "aqi_data.csv"

# Ensure header exists
try:
    with open(CSV_FILE, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "AQI", "Category", "City", "Dominant_Pollutant"])
except FileExistsError:
    pass

def get_category(aqi):
    if aqi <= 50:
        return "Good 🟢"
    elif aqi <= 100:
        return "Satisfactory 🟡"
    elif aqi <= 200:
        return "Moderate 🟠"
    elif aqi <= 300:
        return "Poor 🔴"
    else:
        return "Severe 🚨"

while True:
    for city, (lat, lon) in CITIES.items():
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            response = requests.get(url).json()
            print(f"\n{city} RAW RESPONSE:\n", response)

            aqi_value = response["list"][0]["main"]["aqi"] * 50
            dominant = max(response["list"][0]["components"], key=response["list"][0]["components"].get)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            category = get_category(aqi_value)

            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, aqi_value, category, city, dominant])

            print(f"{city} | AQI: {aqi_value} | {category}")

        except Exception as e:
            print(f"Error fetching {city}:", e)

    print("----- Updating again in 30 seconds -----")
    time.sleep(30)
