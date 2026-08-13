import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import numpy as np
import sys

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
except Exception as e:
    print(f"Failed to open serial port. Error: {e}")
    sys.exit()

fig = plt.figure(facecolor='black')
ax = fig.add_subplot(111, projection='polar', facecolor='black')

ax.set_thetamin(0)
ax.set_thetamax(180)
ax.set_ylim(0, 30)

ax.tick_params(colors='green')
ax.grid(color='green', alpha=0.5)
ax.set_title("STM32 Solid Radar Map (30 cm)", color='lime', weight='bold', pad=20)

angles = np.arange(0, 181, 1)
rad_angles = np.radians(angles)

distances = np.full(181, 30.0)

poly = Polygon(np.column_stack((rad_angles, distances)), facecolor='red', alpha=0.7, edgecolor='none')
ax.add_patch(poly)

scan_line, = ax.plot([], [], color='lime', linewidth=3)

def update(frame):
    if ser.in_waiting > 0:
        try:
            line_data = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if "Distance:" in line_data:
                parts = line_data.split(',')
                if len(parts) == 2:
                    angle_val = int(parts[0].split(':')[1])
                    distance_val = int(parts[1].split(':')[1])
                    
                    if 0 <= angle_val <= 180:
                        start_idx = max(0, angle_val - 2)
                        end_idx = min(181, angle_val + 3)
                        
                        if distance_val > 30:
                            distance_val = 30
                            
                        distances[start_idx:end_idx] = distance_val
                        
                        inner_curve = np.column_stack((rad_angles, distances))
                        outer_curve = np.column_stack((rad_angles[::-1], np.full(181, 30.0)))
                        poly_verts = np.vstack((inner_curve, outer_curve))
                        
                        poly.set_xy(poly_verts)
                        scan_line.set_data([0, np.radians(angle_val)], [0, 30])
                        
        except Exception:
            pass
            
    return poly, scan_line

ani = animation.FuncAnimation(fig, update, interval=15, blit=True, cache_frame_data=False)
plt.show()