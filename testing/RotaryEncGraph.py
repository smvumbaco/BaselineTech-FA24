import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Set up the serial connection
try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # Update port as needed
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error: Could not open serial port. {e}")
    sys.exit(1)

# Initialize lists to hold data
x_data = []
y_data = []
start_time = time.time()

# Define the pitch factor to simulate how pitch impacts speed
pitch_factor = 1.0  # Adjust this as needed to simulate snowboard pitch impact

# Function to update the y-axis based on pitch
def calculate_y_value(time_elapsed):
    # Example: y = pitch_factor * time_elapsed, you can add complexity here
    return pitch_factor * time_elapsed

# Function to update the plot in real-time
def update(frame):
    if ser.in_waiting > 0:  # Check if there is data waiting in the serial buffer
        line = ser.readline().decode('utf-8').strip()
        if line.isdigit():
            raw_value = int(line)
            x_value = raw_value  # Set raw sensor value as x-axis value
            y_value = calculate_y_value(time.time() - start_time)  # Calculate based on pitch

            x_data.append(x_value)
            y_data.append(y_value)

            x_data_plot = x_data[-50:]
            y_data_plot = y_data[-50:]

            ax.clear()
            ax.plot(x_data_plot, y_data_plot, label="Simulated Snowboard Speed")
            ax.set_title("Real-Time Snowboard Simulation")
            ax.set_xlabel("Left-Right Position (X-axis)")
            ax.set_ylabel("Speed based on Pitch (Y-axis)")
            ax.legend()
            ax.grid()

# Set up the plot
fig, ax = plt.subplots()
ani = FuncAnimation(fig, update, interval=10)  # Update every 10ms

plt.show()

# Close the serial connection when done
ser.close()
