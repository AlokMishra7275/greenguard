import requests
import time
import csv
from datetime import datetime

# ---------------- CITY CONFIG ----------------
CITIES = {
    "Delhi": (28.61, 77.23),
    "Mumbai": (19.07, 72.87),
    "Bangalore": (12.97, 77.59),
    "Chennai": (13.08, 80.27),
    "Kolkata": (22.57, 88.36)
}

print("Starting multi-city live air monitoring...")

while True:
    for city, (LAT, LON) in CITIES.items():
        try:
            AIR_URL = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=pm2_5"
            WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m"

            # Fetch PM2.5
            air_response = requests.get(AIR_URL, timeout=10)
            air_data = air_response.json()
            pm25 = air_data["current"]["pm2_5"]

            # Fetch Temperature
            try:
                weather_response = requests.get(WEATHER_URL, timeout=10)
                weather_data = weather_response.json()
                temperature = weather_data["current"]["temperature_2m"]
            except:
                temperature = 30  # fallback

            print(f"[{datetime.now()}] {city} | PM2.5: {pm25} | Temp: {temperature}")

            # Append to CSV
            with open("air_data.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([city, pm25, temperature])

        except Exception as e:
            print(f"{city} API Error:", e)

    print("------ Waiting 60 seconds ------\n")
    time.sleep(60)
