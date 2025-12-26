import requests
from datetime import datetime

# -----------------------------
# Data Models
# -----------------------------

class Blanket:
    def __init__(self, name, min_temp, max_temp):
        self.name = name
        self.min_temp = min_temp
        self.max_temp = max_temp

    def is_suitable(self, temp):
        return self.min_temp <= temp <= self.max_temp


class Horse:
    def __init__(self, name, blankets):
        self.name = name
        self.blankets = blankets

    def select_blanket(self, temp):
        for blanket in self.blankets:
            if blanket.is_suitable(temp):
                return blanket.name
        return "No suitable blanket"


# -----------------------------
# Geocoding (Address → GPS)
# -----------------------------

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json"
    }
    headers = {"User-Agent": "HorseBlanketApp/1.0"}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    if not data:
        raise ValueError("Address not found")

    return float(data[0]["lat"]), float(data[0]["lon"])


# -----------------------------
# Weather (Next 24 Hours)
# -----------------------------

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability",
        "forecast_days": 1,
        "timezone": "auto",
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# -----------------------------
# Blanket Decision Logic
# -----------------------------

def analyze_weather(weather_data):
    temps = weather_data["hourly"]["temperature_2m"]
    for temp in temps:
        print(f"temp = {temp}")
    apparent_temps = weather_data["hourly"]["apparent_temperature"]
    rain_probs = weather_data["hourly"]["precipitation_probability"]

    coldest_apparent = min(apparent_temps)
    will_rain = any(prob >= 50 for prob in rain_probs)

    return coldest_apparent, will_rain


# -----------------------------
# Main App Logic
# -----------------------------

def main():
    address = input("Enter your address: ")

    horses = [
        Horse(
            "Jag",
            [
                Blanket("Heavy Winter Blanket", -20, 20),
                Blanket("Medium Blanket", 21, 40),
                Blanket("Light Sheet", 41, 60),
            ],
        ),
        Horse(
            "Alfie",
            [
                Blanket("Heavy Winter Blanket", -20, 15),
                Blanket("Medium Blanket", 16, 35),
                Blanket("Light Sheet", 36, 55),
            ],
        ),
        Horse(
            "Eugene",
            [
                Blanket("Heavy Winter Blanket", -20, 15),
                Blanket("Medium Blanket", 16, 35),
                Blanket("Light Sheet", 36, 55),
            ],
        ),
    ]

    print("📍 Geocoding address...")
    lat, lon = geocode_address(address)
    print(f"lat = {lat}")
    print(f"lon = {lon}")
    
    print("🌦 Fetching weather...")
    weather = get_weather(lat, lon)

    coldest_temp, will_rain = analyze_weather(weather)

    print("\n🐴 Blanket Recommendations")
    print("----------------------------")

    if will_rain:
        print("🌧 Rain is forecast in the next 24 hours.")
        print("➡ Horses should stay inside. No blankets needed.")
        return

    print(f"❄ Coldest wind-chill temperature: {coldest_temp:.1f}°F\n")

    for horse in horses:
        blanket = horse.select_blanket(coldest_temp)
        print(f"{horse.name}: {blanket}")


# -----------------------------
# Run App
# -----------------------------

if __name__ == "__main__":
    main()
    