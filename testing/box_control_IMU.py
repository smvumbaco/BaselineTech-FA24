import pygame
from pygame.locals import *
import serial
import math

# Serial connection setup
ser = serial.Serial('/dev/tty.usbmodem14301', 38400, timeout=1)  # Update port if necessary

# Global variables
ax = ay = az = 0.0
yaw_mode = False

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

def draw_cube(screen, pitch, roll, yaw):
    # Define cube corners in 3D space
    size = 50  # Cube size
    points = [
        [-size, -size, -size],
        [size, -size, -size],
        [size, size, -size],
        [-size, size, -size],
        [-size, -size, size],
        [size, -size, size],
        [size, size, size],
        [-size, size, size]
    ]

    # Apply rotations based on pitch, roll, and yaw
    rotated_points = []
    for x, y, z in points:
        # Rotate around X-axis (pitch)
        x1 = x
        y1 = y * math.cos(math.radians(pitch)) - z * math.sin(math.radians(pitch))
        z1 = y * math.sin(math.radians(pitch)) + z * math.cos(math.radians(pitch))

        # Rotate around Y-axis (roll)
        x2 = x1 * math.cos(math.radians(roll)) + z1 * math.sin(math.radians(roll))
        y2 = y1
        z2 = -x1 * math.sin(math.radians(roll)) + z1 * math.cos(math.radians(roll))

        # Rotate around Z-axis (yaw)
        x3 = x2 * math.cos(math.radians(yaw)) - y2 * math.sin(math.radians(yaw))
        y3 = x2 * math.sin(math.radians(yaw)) + y2 * math.cos(math.radians(yaw))
        z3 = z2

        # Project 3D points to 2D
        screen_x = CENTER_X + int(x3)
        screen_y = CENTER_Y - int(y3)
        rotated_points.append((screen_x, screen_y))

    # Define edges of the cube
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connections
    ]

    # Draw edges
    for edge in edges:
        pygame.draw.line(screen, (255, 255, 255), rotated_points[edge[0]], rotated_points[edge[1]], 2)

def read_data():
    global ax, ay, az
    try:
        ser.write(b".")  # Request data
        line = ser.readline().strip()
        angles = line.split(b", ")
        if len(angles) == 3:
            ax = float(angles[0])
            ay = float(angles[1])
            az = float(angles[2])
    except Exception as e:
        print(f"Error reading serial data: {e}")

def main():
    global yaw_mode

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("3D Cube Visualization")
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

        # Draw the cube
        draw_cube(screen, ay, ax, az if yaw_mode else 0)

        # Display text
        font = pygame.font.SysFont("Courier", 18, True)
        osd_text = f"Pitch: {ay:.2f}, Roll: {ax:.2f}"
        if yaw_mode:
            osd_text += f", Yaw: {az:.2f}"
        text_surface = font.render(osd_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
