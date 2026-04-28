 # =========================================
# STEP 1: Install Libraries
# =========================================
!pip install requests pandas numpy scikit-learn

# =========================================
# STEP 2: Imports
# =========================================
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error # Added for MAE calculation
import seaborn as sns # Added for enhanced plotting

# =========================================
# STEP 3: Convert City → Coordinates
# =========================================
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    res = requests.get(url).json()

    if "results" not in res:
        print("❌ City not found")
        return None

    lat = res["results"][0]["latitude"]
    lon = res["results"][0]["longitude"]

    print(f"ƒ {city} → Lat: {lat}, Lon: {lon}")
    return lat, lon

# =========================================
# STEP 4: Get Historical Weather Data (Modified for hourly data and humidity)
# =========================================
def get_historical_data(lat, lon, target_hour):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730) # Get 2 years of data
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date_str}&end_date={end_date_str}"
        f"&hourly=temperature_2m,relative_humidity_2m" # Request hourly temperature and humidity
    )

    data = requests.get(url).json()

    if "hourly" not in data or "temperature_2m" not in data["hourly"] or "relative_humidity_2m" not in data["hourly"]:
        print(f"❌ No hourly temperature or humidity data found for historical records between {start_date_str} and {end_date_str}.")
        return pd.DataFrame()

    hourly_data = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "temperature": data["hourly"]["temperature_2m"],
        "humidity": data["hourly"]["relative_humidity_2m"]
    })

    # Filter for the target hour
    hourly_data['hour'] = hourly_data['time'].dt.hour
    df_filtered = hourly_data[hourly_data['hour'] == target_hour].copy()

    # Sort by time to ensure correct shifting
    df_filtered = df_filtered.sort_values(by="time").reset_index(drop=True)

    # Create targets (next day temp and humidity at the same hour)
    df_filtered["next_day_temp"] = df_filtered["temperature"].shift(-1)
    df_filtered["next_day_humidity"] = df_filtered["humidity"].shift(-1)
    df_filtered.rename(columns={
        "temperature": "current_hour_temp",
        "humidity": "current_hour_humidity"
    }, inplace=True)
    df_filtered.dropna(inplace=True)

    return df_filtered[["time", "current_hour_temp", "current_hour_humidity", "next_day_temp", "next_day_humidity"]]

# New helper function to get historical data for a range of hours
def get_historical_data_for_hours_range(lat, lon, hours_list):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730) # Get 2 years of data
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date_str}&end_date={end_date_str}"
        f"&hourly=temperature_2m,relative_humidity_2m" # Request hourly temperature and humidity
    )

    data = requests.get(url).json()

    if "hourly" not in data or "temperature_2m" not in data["hourly"] or "relative_humidity_2m" not in data["hourly"]:
        print(f"❌ No hourly temperature or humidity data found for historical records between {start_date_str} and {end_date_str}.")
        return pd.DataFrame()

    hourly_data = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "temperature": data["hourly"]["temperature_2m"],
        "humidity": data["hourly"]["relative_humidity_2m"]
    })

    hourly_data['hour'] = hourly_data['time'].dt.hour
    df_filtered_range = hourly_data[hourly_data['hour'].isin(hours_list)].copy()

    return df_filtered_range[["time", "temperature", "humidity", "hour"]]

# =========================================
# STEP 4.1: Get Forecast Weather Data (Modified for humidity)
# =========================================
def get_forecast_data(lat, lon, target_hour):
    # Forecast starts from tomorrow for the next 3 days
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2) # Tomorrow + 2 more days = 3 days forecast

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date_str}&end_date={end_date_str}"
        f"&hourly=temperature_2m,relative_humidity_2m" # Request hourly temperature and humidity
    )
    data = requests.get(url).json()

    if "hourly" not in data or "temperature_2m" not in data["hourly"] or "relative_humidity_2m" not in data["hourly"]:
        print(f"❌ No hourly temperature or humidity data found for forecast between {start_date_str} and {end_date_str}.")
        return pd.DataFrame()

    hourly_data = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "temperature": data["hourly"]["temperature_2m"],
        "humidity": data["hourly"]["relative_humidity_2m"]
    })

    hourly_data['hour'] = hourly_data['time'].dt.hour
    df_filtered = hourly_data[hourly_data['hour'] == target_hour].copy()
    df_filtered.rename(columns={
        "temperature": "current_hour_temp",
        "humidity": "current_hour_humidity"
    }, inplace=True)
    return df_filtered[["time", "current_hour_temp", "current_hour_humidity"]]

# =========================================
# STEP 5: Train ML Model (Modified for multiple input features)
# =========================================
def train_model(df):
    if df.empty:
        print("❌ Cannot train model: Historical data is empty.")
        return None

    X = df[["current_hour_temp", "current_hour_humidity"]] # Changed features to temp and humidity
    y = df["next_day_temp"]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    print(f"✅ Model trained on real historical data for the specific hour")
    return model

# =========================================
# STEP 6: Get LIVE Weather (Modified for humidity)
# =========================================
def get_live_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current_weather=true&hourly=relative_humidity_2m" # Request current humidity as well
    )

    data = requests.get(url).json()
    current = data["current_weather"]
    hourly = data.get("hourly", {})

    temp = current["temperature"]

    # Get current humidity from the hourly data, if available
    # The 'current["time"]' might have minutes, while 'hourly["time"]' has full hours.
    # We need to find the hourly data corresponding to the current hour.
    current_datetime = datetime.fromisoformat(current["time"])
    current_hour_str = current_datetime.strftime("%Y-%m-%dT%H:00")

    humidity = None
    for i, hourly_time_str in enumerate(hourly["time"]):
        if hourly_time_str == current_hour_str:
            humidity = hourly["relative_humidity_2m"][i]
            break

    if humidity is None:
        print(f"❌ Could not find humidity data for current hour: {current_hour_str}")
        # Fallback if exact match not found (e.g., if API returns different time formats)
        # For now, we'll return None for humidity if not found
        return temp, None

    print(f"\nK Current Temp: {temp} °C, Humidity: {humidity} %")

    return temp, humidity

# =========================================
# STEP 7: MAIN PIPELINE (Modified)
# =========================================
city = input("Enter City Name: ")

coords = get_coordinates(city)

if coords:
    lat, lon = coords

    current_hour = datetime.now().hour # Get the current hour

    print(f"Fetching historical data for hour: {current_hour}:00")
    df = get_historical_data(lat, lon, current_hour)
    if df.empty:
        print("Cannot proceed without sufficient historical data for the current hour. Please try again later or with a different city/time.")
    else:
        model = train_model(df)

        if model:
            # Calculate MAE immediately after training the model
            X_hist = df[["current_hour_temp", "current_hour_humidity"]]
            y_hist_pred = model.predict(X_hist)
            y_hist_actual = df["next_day_temp"]
            mae = mean_absolute_error(y_hist_actual, y_hist_pred)
            print(f"\n📊 Model Mean Absolute Error on Historical Data: {round(mae, 2)} °C")

            current_temp, current_humidity = get_live_weather(lat, lon)

            # Proceed only if current_humidity was successfully retrieved
            if current_humidity is not None:
                # Input data for prediction now includes current hour's temp and humidity
                input_data = pd.DataFrame([[current_temp, current_humidity]], columns=["current_hour_temp", "current_hour_humidity"])
                predicted = model.predict(input_data)

                print("\nʘ Predicted Next Day Temperature (at the same hour):")
                print(f"→ {round(predicted[0], 2)} °C")

                # Insight - adjusted thresholds for hourly temperatures
                if predicted[0] > 30:
                    print("🔥 Hot conditions expected")
                elif predicted[0] < 10:
                    print("❄ Cold conditions expected")
                else:
                    print("⛅ Moderate weather expected")
            else:
                print("❌ Cannot make a prediction without current humidity data.")

# Clean up potentially problematic global variables from previous runs
for var_name in ['data', 'X', 'y']:
    if var_name in globals():
        del globals()[var_name]
