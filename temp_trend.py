# --- Generate an attractive visualization of temperature trends ---

# Get recent historical data (last 3 days) from the existing 'df'
# The 'df' contains historical data up to datetime.now() (minus some hours due to target_hour)
# So, let's filter for the last 3 full days of historical data up to the most recent entry in df.

recent_historical_df = df[df['time'] >= (df['time'].max() - timedelta(days=3))].copy()
recent_historical_df = recent_historical_df[['time', 'current_hour_temp']]

# Prepare current temperature data point
current_time_point = datetime.now().replace(minute=0, second=0, microsecond=0)
current_temp_df = pd.DataFrame([{'time': current_time_point, 'current_hour_temp': current_temp}])

# Get forecast data (next 3 days) at the current_hour
forecast_df = get_forecast_data(lat, lon, current_hour)

# Combine all dataframes for plotting
combined_df = pd.concat([recent_historical_df, current_temp_df, forecast_df[['time', 'current_hour_temp']]], ignore_index=True) # Only take temp for plotting

# Remove potential duplicates at the boundaries and sort by time
combined_df = combined_df.drop_duplicates(subset='time').sort_values('time').reset_index(drop=True)

# Add the predicted next day temperature if available
if 'predicted' in globals() and 'current_hour' in globals():
    predicted_next_day_time = (datetime.now() + timedelta(days=1)).replace(hour=current_hour, minute=0, second=0, microsecond=0)
    # Check if this predicted time is already covered by forecast_df to avoid duplicate markers
    if predicted_next_day_time not in combined_df['time'].values:
        predicted_next_day_temp_df = pd.DataFrame([{'time': predicted_next_day_time, 'current_hour_temp': predicted[0]}]
        )
        combined_df = pd.concat([combined_df, predicted_next_day_temp_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset='time').sort_values('time').reset_index(drop=True)

# Plotting
plt.figure(figsize=(15, 7))
plt.style.use('seaborn-v0_8-darkgrid') # Use a nice style for the plot

# Plot the main temperature trend
plt.plot(combined_df['time'], combined_df['current_hour_temp'], marker='o', linestyle='-', color='#1f77b4', label='Temperature Trend') # Changed line color

# Highlight current temperature point
plt.scatter(current_time_point, current_temp, color='green', s=100, zorder=5, label='Current Temperature')

# Highlight the predicted next day temperature point (if added)
if 'predicted' in globals() and 'current_hour' in globals() and predicted_next_day_time in combined_df['time'].values:
    plt.scatter(predicted_next_day_time, predicted[0], color='red', marker='X', s=150, zorder=5, label='Next Day Prediction')

# Add vertical lines to delineate historical, current, and forecast periods
today_start = datetime.now().replace(hour=current_hour, minute=0, second=0, microsecond=0)
plt.axvline(x=today_start, color='orange', linestyle='--', linewidth=1, label='Today') # Changed line color
plt.axvline(x=today_start + timedelta(days=1), color='purple', linestyle=':', linewidth=1, label='Prediction Start')

plt.title(f'Temperature Trends for {city} at {current_hour}:00 (Historical, Current, Forecast)', fontsize=16)
plt.xlabel('Date and Time', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
