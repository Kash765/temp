from picamera2 import Picamera2, Preview
import time
from gpiozero import AngularServo


#camera test

'''picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(2)
picam2.capture_file("test.jpg")'''

servo1 = AngularServo(0, min_pulse_width=0.0009, max_pulse_width=0.0011)
servo2 = AngularServo(1, min_pulse_width=0.0009, max_pulse_width=0.0011)

def move_servos_slow(angle, step=1, delay=0.03):
    """
    target_angle : final angle (-90 to 90)
    step         : degrees per step (smaller = slower)
    delay        : pause between steps (larger = slower)
    """

    current = servo1.angle or 0  # handle startup None

    
    servo1.angle = angle
    servo2.angle = -angle   # inverted servo

while True:
    move_servos_slow(45, step=1, delay=0.3)
    time.sleep(1)