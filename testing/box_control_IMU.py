import pygame
from pygame.locals import *
import serial
import math
import struct

# Serial connection setup
ser = serial.Serial('/dev/tty.usbmodem14101', 38400, timeout=1)  # Update port if necessary

# Global variables for IMU data
ax = ay = az = 0.0  # Accelerometer axes
yaw_mode = False    # Toggle for yaw data display

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Scaling factors for accelerometer and gyroscope data
ACCEL_SCALE = 1 / 16384.0  # Example for ±2g range
GYRO_SCALE = 1 / 131.0     # Example for ±250°/s range

def draw_rectangle(screen, pitch, roll, yaw):
    """
    Draws a rectangle rotated based on IMU pitch, roll, and yaw data.
    """
    width, height = 200, 100  # Rectangle dimensions
    color = (255, 255, 255)  # Rectangle color

    # Calculate rotation using yaw (rotation around Z-axis for 2D visualization)
    rect_points = [
        [-width / 2, -height / 2],
        [width / 2, -height / 2],
        [width / 2, height / 2],
        [-width / 2, height / 2]
    ]

    rotated_points = []
    for x, y in rect_points:
        # Apply 2D rotation using yaw
        x_rotated = x * math.cos(math.radians(yaw)) - y * math.sin(math.radians(yaw))
        y_rotated = x * math.sin(math.radians(yaw)) + y * math.cos(math.radians(yaw))

        # Project to screen coordinates
        screen_x = CENTER_X + int(x_rotated)
        screen_y = CENTER_Y - int(y_rotated)
        rotated_points.append((screen_x, screen_y))

    # Draw the rectangle by connecting its corners
    pygame.draw.polygon(screen, color, rotated_points, 2)

def read_data():
    """
    Reads and decodes IMU binary data from the serial port.
    Updates global ax, ay, az variables with accelerometer data.
    """
    global ax, ay, az
    try:
        ser.write(b".")  # Request data
        raw_data = ser.read(36)  # Adjust based on IMU output size
        if len(raw_data) == 36:  # Ensure we received enough data
            # Decode as 16-bit signed integers (little-endian)
            decoded_values = struct.unpack('<18h', raw_data)
            
            # Extract accelerometer and gyroscope values
            accel_x, accel_y, accel_z = decoded_values[0:3]  # First 3 are accelerometer
            gyro_x, gyro_y, gyro_z = decoded_values[3:6]     # Next 3 are gyroscope
            print(decoded_values)
            
            # Scale values
            ax = accel_x * ACCEL_SCALE
            ay = accel_y * ACCEL_SCALE
            az = accel_z * ACCEL_SCALE
    except Exception as e:
        print(f"Error reading serial data: {e}")

def main():
    global yaw_mode

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("IMU Visualization")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            if event.type == KEYDOWN and event.key == K_z:
                yaw_mode = not yaw_mode
                ser.write(b"z")  # Toggle yaw mode on the IMU

        # Read data from serial
        read_data()

        # Clear screen
        screen.fill((0, 0, 0))

        # Use accelerometer Y (pitch), X (roll), and Z (yaw if enabled) for rotation
        draw_rectangle(screen, ay, ax, az if yaw_mode else 0)

        # Display text
        font = pygame.font.SysFont("Courier", 18, True)
        osd_text = f"Pitch: {ay:.2f}g, Roll: {ax:.2f}g"
        if yaw_mode:
            osd_text += f", Yaw: {az:.2f}g"
        text_surface = font.render(osd_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
