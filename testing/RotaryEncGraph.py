import serial
import time
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading

# Set up the serial connection
try:
    ser = serial.Serial('/dev/tty.usbmodem14301', 115200, timeout=1)  # Update port as needed
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error: Could not open serial port. {e}")
    sys.exit(1)

# Shared data buffers
x_data = deque(maxlen=500)
y_data = deque(maxlen=500)
start_time = time.time()
running = True  # Flag to control the serial thread

# Define the pitch factor to simulate how pitch impacts speed
pitch_factor = 1.0

# Function to calculate y-axis value
#def calculate_y_value(time_elapsed):
    #return pitch_factor * time_elapsed

# Serial reading in a separate thread
def read_serial():
    while running:  # Keep reading while the program is running
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.isdigit():
                    raw_value = int(line)
                    x_data.append(raw_value)
                    #y_data.append(calculate_y_value(time.time() - start_time))
                    y_data.append(time.time() - start_time)
            except Exception as e:
                if running:  # Only print errors if the program is still running
                    print(f"Error reading serial data: {e}")

# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# Function to update the plot
def update(frame):
    x_data_plot = list(x_data)[-50:]  # Last 50 points
    y_data_plot = list(y_data)[-50:]

    if len(x_data_plot) > 0 and len(y_data_plot) > 0:
        ax.clear()
        ax.plot(x_data_plot, y_data_plot, label="Simulated Snowboard Location")
        ax.set_title("Real-Time Snowboard Simulation")
        ax.set_xlabel("Left-Right Position (X-axis)")
        ax.set_ylabel("Speed based on Pitch (Y-axis)")
        ax.set_xlim(0, 1050)  # Fixed x-axis range        
        ax.legend()
        ax.grid()

# Function to safely close the serial port and stop the thread
def close_serial():
    global running
    running = False  # Signal the thread to stop
    serial_thread.join()  # Wait for the thread to finish
    ser.close()  # Close the serial port
    print("Serial port closed.")

# Set up the plot
fig, ax = plt.subplots()
ani = FuncAnimation(fig, update, interval=1*pitch_factor)    #update every 1ms

# Hook into the closing event of the plot
def on_close(event):
    close_serial()  # Clean up when the plot window is closed

fig.canvas.mpl_connect('close_event', on_close)

plt.show()