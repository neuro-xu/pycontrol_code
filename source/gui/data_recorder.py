import sys
import serial
import cv2
import csv
import os
import time
import signal
import multiprocessing
from datetime import datetime

# --- Configuration ---
SERIAL_PORT = 'COM3'   
BAUD_RATE = 115200
OUTPUT_DIR = "data_logs"
CAMERA_INDEX = 0
VIDEO_RES = (640, 480)

# Global flag for the signal handler to stop the loop
stop_event = multiprocessing.Event()

def video_process(filename_base, stop_event):
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_RES[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_RES[1])
    
    # Save as AVI
    video_path = os.path.join(OUTPUT_DIR, f"{filename_base}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, VIDEO_RES)
    
    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                time.sleep(0.001)
    finally:
        # This runs when stop_event is set
        out.release()
        cap.release()

def serial_process(filename_base, stop_event):
    csv_path = os.path.join(OUTPUT_DIR, f"{filename_base}.csv")
    
    try:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            
            while not stop_event.is_set():
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    row = line.split(',')
                    row.insert(0, datetime.now().strftime('%H:%M:%S.%f'))
                    writer.writerow(row)
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(str(e))

if __name__ == "__main__":
    # 1. Get Subject ID from Command Line args (passed by GUI)
    if len(sys.argv) > 1:
        subject_id = sys.argv[1]
    else:
        subject_id = "TEST"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Create timestamped filename
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{subject_id}_{ts}"

    # 2. Setup Processes
    p_vid = multiprocessing.Process(target=video_process, args=(filename, stop_event))
    p_ser = multiprocessing.Process(target=serial_process, args=(filename, stop_event))

    p_vid.start()
    p_ser.start()

    # 3. Handle Exit Signal from GUI
    # When GUI sends .terminate(), Python catches it here
    def clean_exit(signum, frame):
        stop_event.set() # Tell children to finish up
        p_vid.join()
        p_ser.join()
        sys.exit(0)

    signal.signal(signal.SIGTERM, clean_exit)
    signal.signal(signal.SIGINT, clean_exit)

    # Keep main process alive waiting for the kill signal
    while True:
        time.sleep(1)