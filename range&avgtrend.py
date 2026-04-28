# Calculate the hours range (current hour, 3 hours before, 3 hours after)

current_hour = datetime.now().hour
hours_list = [(current_hour - i + 24) % 24 for i in range(3, 0, -1)] + [current_hour] + [(current_hour + i) % 24 for i in range(1, 4)]
hours_list = sorted(list(set(hours_list))) # Remove duplicates and sort

print(f"Analyzing historical data for hours: {hours_list}")

# Fetch historical data for the specified range of hours
hist_range_df = get_historical_data_for_hours_range(lat, lon, hours_list)
display(hist_range_df.head())


import matplotlib.pyplot as plt
import seaborn as sns

# Calculate average temperature and humidity for each hour in the range

avg_trends_df = hist_range_df.groupby('hour')[['temperature', 'humidity']].mean().reset_index()

# Ensure all hours from hours_list are present, fill missing with NaN for plotting consistency
all_hours_df = pd.DataFrame({'hour': hours_list})
avg_trends_df = pd.merge(all_hours_df, avg_trends_df, on='hour', how='left')

# Sort by hour for proper plotting
avg_trends_df = avg_trends_df.sort_values(by='hour').reset_index(drop=True)

# Plotting
fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True) # Two subplots, sharing x-axis
plt.style.use('seaborn-v0_8-darkgrid')

# Plot Average Historical Temperature Trend
sns.lineplot(ax=axes[0], x='hour', y='temperature', data=avg_trends_df, marker='o', color='red', label='Average Temperature')
axes[0].axvline(x=current_hour, color='blue', linestyle='--', label='Current Hour')
axes[0].set_title(f'Average Historical Temperature Trend for {city} (Past 3, Current, Next 3 hours)', fontsize=16)
axes[0].set_ylabel('Average Temperature (°C)', fontsize=12)
axes[0].legend()
axes[0].grid(True, linestyle='--', alpha=0.6)

# Plot Average Historical Humidity Trend
sns.lineplot(ax=axes[1], x='hour', y='humidity', data=avg_trends_df, marker='o', color='green', label='Average Humidity')
axes[1].axvline(x=current_hour, color='blue', linestyle='--', label='Current Hour')
axes[1].set_title(f'Average Historical Humidity Trend for {city} (Past 3, Current, Next 3 hours)', fontsize=16)
axes[1].set_xlabel('Hour of Day', fontsize=12)
axes[1].set_ylabel('Average Humidity (%)', fontsize=12)
axes[1].set_xticks(hours_list) # Set x-ticks to only the hours in the list
axes[1].set_xticklabels([f'{h:02d}:00 hr' for h in hours_list]) # Format x-axis labels
axes[1].legend()
axes[1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()
