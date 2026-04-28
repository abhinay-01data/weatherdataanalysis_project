# =========================================

# Historical Temperature and Humidity at Current Hour

# =========================================

plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['current_hour_temp'])
plt.title('Historical Temperature at Current Hour')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['current_hour_humidity'], color='orange')
plt.title('Historical Humidity at Current Hour')
plt.xlabel('Date')
plt.ylabel('Humidity (%)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
