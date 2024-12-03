import serial
import time
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading
import numpy as np  

#Ava Gami rotary encoder BaselineTech code
#creates graph simulating the snowboarder's position on the snow 
#for testing purposes separate of snowboarding simulator, align blue tick mark on encoder with tick in casing. first reading should be ~605 if aligned properly 

# Set up the serial connection
try:
    ser = serial.Serial('/dev/tty.usbmodem14101', 115200, timeout=1)  # update port as needed
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error: Could not open serial port. {e}")
    sys.exit(1)
    
    
pitch_factor = 1.0          # USER: define the pitch factor based on snowboard pitch 


# Shared data buffers
x_data = deque(maxlen=500)
y_data = deque(maxlen=500)
start_time = time.time()
running = True  # Flag to control the serial thread

# Add a thread lock
data_lock = threading.Lock()

# Add a variable to track the last valid value
last_valid_value = None

set_origin = 0;
origin = 0;
pos = 0;

# Function to calculate y-axis value
def calculate_y_value(time_elapsed):
    return pitch_factor * time_elapsed

# Function to calculate moving average
def moving_average(data, window_size=5):
    if len(data) < window_size:
        return data  # Not enough data to smooth
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Serial reading in a separate thread
def read_serial():
    global last_valid_value, set_origin, origin, pos 
    while running:
        try:
            data = ser.read(ser.in_waiting).decode('utf-8').strip()  # Read all available data
            lines = data.split("\n")
            with data_lock:
                for line in lines:
                    if line.isdigit():
                        raw_value = int(line)
                        print(raw_value-origin)
                        
                        if set_origin == 0:     #get original value, use as central point 
                            origin = raw_value
                            set_origin = 1      #origin only gets set once, at beginning of run
                        
                        if last_valid_value is None:        #init last valid value at begin of run 
                            last_valid_value = raw_value                        

                        #check for unexpected readings and ignore if bad (difference over 200 but below 900 to preserve 0 to 1024 continuity)
                        if abs(last_valid_value - raw_value) > 200 and abs(last_valid_value - raw_value) < 900:
                            raw_value = last_valid_value
                        else:
                            last_valid_value = raw_value        #if it was within expected range, update the last valid value  
                            
                        #adjust the scale factor as needed for sensitivity, likely after testing. 25-50 range seems optimal 
                        pos = (pos) + (raw_value-origin)/25      #calculate pos based off previous position and deviation of encoder from 'origin' 

                        # Append valid data to be plotted 
                        x_data.append(pos)
                        y_data.append(calculate_y_value(time.time() - start_time))
        except Exception as e:
            if running:
                print(f"Error reading serial data: {e}")
        time.sleep(0.002)
# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# Function to update the plot
def update(frame):
    with data_lock:  # Lock access to shared data
        x_data_plot = list(x_data)[-50:]  # Last 50 points
        y_data_plot = list(y_data)[-50:]

    if len(x_data_plot) > 0 and len(y_data_plot) > 0:
        # Apply smoothing to y_data
        y_data_smooth = moving_average(y_data_plot, window_size=5)

        # Ensure x_data matches the length of smoothed y_data
        x_data_smooth = x_data_plot[-len(y_data_smooth):]

        ax.clear()
        ax.plot(x_data_smooth, y_data_smooth)
        ax.set_title("Real-Time Snowboard Simulation")
        ax.set_xlabel("Left-Right Position (X-axis)")
        ax.set_ylabel("Speed based on Pitch (Y-axis)")
        ax.set_xlim(-100, 100)  # Fixed x-axis range
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
ani = FuncAnimation(fig, update, interval=1)    #update every 1ms

# Hook into the closing event of the plot
def on_close(event):
    close_serial()  # Clean up when the plot window is closed

fig.canvas.mpl_connect('close_event', on_close)

plt.show()
