# =========================================
# Interpreting the Mean Absolute Error (MAE)


# The Mean Absolute Error (MAE) calculated above represents the average absolute difference between the actual next day's temperature 
# and our model's predicted next day's temperature.
# For example, an MAE of 2.5 °C means that, on average, our predictions are off by 2.5 °C from the actual temperature. 
# A lower MAE indicates a more accurate model.

# =========================================


if 'mae' in locals():
    print(f"The calculated Mean Absolute Error (MAE) is: {round(mae, 2)} °C")
else:
    print("MAE has not been calculated yet. Please ensure the MAE calculation cell has been run.")
