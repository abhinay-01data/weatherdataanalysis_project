# =========================================

# Actual vs. Predicted Next Day Temperature (Historical Data)

# ========================================= 


if 'model' in locals() and model is not None and not df.empty:
    X_hist = df[["current_hour_temp", "current_hour_humidity"]]
    y_hist_pred = model.predict(X_hist)
    y_hist_actual = df["next_day_temp"]

    plt.figure(figsize=(10, 8))
    plt.scatter(y_hist_actual, y_hist_pred, alpha=0.6, color='blue', label='Predictions')
    plt.plot([y_hist_actual.min(), y_hist_actual.max()], [y_hist_actual.min(), y_hist_actual.max()], 'r--', label='Ideal Prediction (Actual = Predicted)')
    plt.title('Actual vs. Predicted Next Day Temperature (Historical Data)', fontsize=14)
    plt.xlabel('Actual Next Day Temperature (°C)', fontsize=12)
    plt.ylabel('Predicted Next Day Temperature (°C)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("Cannot plot actual vs. predicted: model not trained or historical data is empty.")
