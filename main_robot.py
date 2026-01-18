import cv2
import time
from collections import deque
from picamera2 import Picamera2
import sounddevice as sd
import soundfile as sf
from gpiozero import AngularServo
from Detector import Detector
from PomodoroTimer import PomodoroTimer
from ExpressionMaker import ExpressionMaker
from WebSettings import WebSettings

WINDOW_SIZE = 5
PHONE_THRESHOLD = 3
FACE_THRESHOLD = 3

# This is a guess
FRAME_WIDTH = 640
AUDIO_PATH = "/home/antisocialartificers/Downloads/youridol.wav"

class DetectionSmoother:
    # Keep majority/threshold vote over last window_size frames
    def __init__(self, window_size=WINDOW_SIZE):
        self.window_size = window_size
        self.face_history = deque(maxlen=window_size)
        self.phone_history = deque(maxlen=window_size)

    def update(self, face_detections, phone_detections):
        has_face = len(face_detections["faces"]) > 0
        has_phone = len(phone_detections["phones"]) > 0

        self.face_history.append(has_face)
        self.phone_history.append(has_phone)

    def get_smoothed_state(self, face_threshold=FACE_THRESHOLD, phone_threshold=PHONE_THRESHOLD):
        face_count = sum(self.face_history)
        phone_count = sum(self.phone_history)

        face_present = face_count >= face_threshold
        phone_present = phone_count >= phone_threshold

        return face_present, phone_present

def is_working(face_present, phone_present):
    if not face_present: 
        return False
    if phone_present:
        return False
    return True

def crash_out_move(init_face_detections, servo, servo2, picam2, face_detector, expression_handler, mode=None, timestamp=None, is_playing = True):
    print("CRASHING OUT NOW")

    expression_handler.sad(mode, timestamp)
    data, fs = sf.read(AUDIO_PATH, dtype="float32")
    if not is_playing:
        is_playing = True 
        sd.play(data, fs)

    if(not init_face_detections or len(init_face_detections["faces"]) == 0):
        servo.angle = 0
        time.sleep(0.15)
        servo.value = None
        return is_playing

    # crash out (shake)
    for i in range(4):
        servo.angle = 45
        servo2.angle = 45
        time.sleep(0.05)
        servo.angle = -45
        servo2.angle = -45
        time.sleep(0.05)

    #frame_center_x = frame_width // 2

    '''for angle in range(-90, 91, 1): # rotate 5 degrees per step
        print("ROTATING UP TO ANGLE: %d\n", angle)
        servo.angle = max(-90, min(90, angle))
        servo2.angle = max(-90, min(90, angle))
        time.sleep(1)

        frame = picam2.capture_array()
        frame_width = frame.shape[1]

        face_detections = face_detector.detect(frame)

        if len(face_detections["faces"]) > 0:
            main_face = face_detections["faces"][0]
            x1, y1, x2, y2 = map(int, main_face)
            face_center_x = (x1 + x2) // 2
            
            if abs(face_center_x - (frame_width // 2)) < 50:
                servo.angle = 0
                servo2.angle = 0
                time.sleep(0.15)
                servo.value = None
                servo2.value = None
                return is_playing '''
    
    servo.angle = 0
    servo2.angle = 0
    servo.value = None 
    servo2.value = None
    
    return is_playing
            
def main():
    is_playing = False 

    # Initialize Picamera2 for streaming
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # Initialize servo
    servo = AngularServo(0, min_pulse_width=0.0009, max_pulse_width=0.0021)
    servo2 = AngularServo(1, min_pulse_width=0.0009, max_pulse_width=0.0021)
    servo.angle = 0
    servo2.angle = 0
    servo.value = None 
    servo2.value = None

    face_detector = Detector()
    phone_detector = Detector("phone_best.pt")
    smoother = DetectionSmoother(WINDOW_SIZE)
    expression_handler = ExpressionMaker()
    
    # don't start until you see a face
    session_started = False
    pomodoro = None

    def on_settings_changed(settings):
        if pomodoro is not None:
            pomodoro.set_times(settings['pomodoro_work'], settings['pomodoro_break'])

    web_settings = WebSettings(port=5000, on_settings_changed=on_settings_changed)
    web_settings.start()

    try:
        while True:
            # Capture frame from Picamera2
            frame = picam2.capture_array()

            face_detections = face_detector.detect(frame)
            phone_detections = phone_detector.detect(frame)

            # Update smoother with current frame's detections
            smoother.update(face_detections, phone_detections)

            # draw phone bounding boxes
            for box in phone_detections["phones"]:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "phone", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # draw face bounding boxes
            for box in face_detections["faces"]:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "face", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # get smoothed state and determine if working
            face_present, phone_present = smoother.get_smoothed_state()

            # Start session when first face is detected
            if not session_started and face_present:
                session_started = True
                pomodoro = PomodoroTimer()

            # If session hasn't started yet, show waiting state
            if not session_started:
                status_text = "WAITING FOR FACE"
                status_color = (128, 128, 128)  # gray
                cv2.putText(frame, status_text, (10, 55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                cv2.putText(frame, "Session will start when face detected", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                cv2.imshow('Object Detection', frame)
                print(status_text)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            working = is_working(face_present, phone_present)
            on_break = pomodoro.is_break_time()

            # calculate mode and timestamp for display
            mode = 'B' if on_break else 'W'
            remaining = pomodoro.get_time_remaining()
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"

            if not working and not on_break:
                is_playing = crash_out_move(face_detections, servo, servo2, picam2, face_detector, expression_handler, mode, timestamp, is_playing)
            else:
                expression_handler.sleepy(mode, timestamp)
                if is_playing:
                    try:
                        stream = sd.get_stream()
                        if stream is not None and stream.active:
                            sd.stop()
                            is_playing = False
                    except Exception as e:
                        print("bleh")

            # display status
            if on_break:
                status_text = "BREAK TIME"
                status_color = (0, 255, 255)  # yellow
            elif not working:
                status_text = "NOT WORKING"
                status_color = (0, 0, 255)  # red
            else:
                status_text = "working"
                status_color = (255, 255, 255)  # white
            cv2.putText(frame, status_text, (10, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

            # display Pomodoro timer
            timer_text = pomodoro.get_status_string()
            cv2.putText(frame, timer_text, (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            cv2.imshow('Object Detection', frame)

            print(f"{status_text} | {timer_text}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()