import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
import math
from collections import deque
import csv
import sys
from pathlib import Path
import imageio
import subprocess
import os
from config_manager import ConfigManager

# # Choose which two fingers to check:
# FINGER_A = 8   # index tip
# FINGER_B = 4   # thumb tip

# # Parameters
# RELATIVE_TOUCH_THRESHOLD = 0.15  # relative to hand bbox diagonal
# DEBOUNCE_FRAMES = 2
# SMOOTHING_WINDOW = 1
# FPS = 60

class TapPositions:
    def __init__(self, input_dir, output_dir, first_run=False, config_path="config.json"):
        print("New tap positions!")

        cfg = ConfigManager(config_path).get_class_config("TapPositions")

        self.FINGER_A = cfg["FINGER_A"]
        self.FINGER_B = cfg["FINGER_B"]
        self.rel_touch_thresh = cfg["RELATIVE_TOUCH_THRESHOLD"]
        self.debounce = cfg["DEBOUNCE_FRAMES"]
        self.smooth_window = cfg["SMOOTHING_WINDOW"]
        self.fps = cfg["FPS"]

        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.first_run = first_run
    def process_directory(self):
        print("Processing directory...")
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='./model/hand_landmarker.task'),
            running_mode=RunningMode.IMAGE)
        hands = HandLandmarker.create_from_options(options)
        if not self.input_dir.is_dir():
            print("Provided path is not a folder!")
            sys.exit(1)

        # Get all .webm files in folder
        video_files = list(self.input_dir.glob("*.webm"))
        if not video_files:
            print("No .webm files found in folder.")
            sys.exit(1)

        def euclid(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])
        aggregate_csv_path =  self.output_dir / "aggregate_tap.csv"
        aggregate_csv_writer = csv.writer(open(aggregate_csv_path, "w", newline=''))
        aggregate_csv_writer.writerow(['timeElapsed', 'relDist', 'isTouch', 'participantID', 'task', 'audio', 'block', 'trial', 'tapEvent'])
        for video_path in video_files:
            vidvals = str(video_path.name).split("_")
            print(f"Processing {video_path.name}")
            if self.first_run:
                subprocess.run([
                    "ffmpeg",
                    "-y",                    # overwrite temp file if it exists
                    "-i", str(video_path),
                    "-vf", "fps=60",
                    "-vsync", "cfr",
                    "-c:v", "libvpx",        # VP8/VP9 encoder for webm
                    "-c:a", "copy",          # keep audio as-is
                    "tempvideo.webm"
                ], check=True)

                # Replace original file
                os.replace("tempvideo.webm", video_path)
            try:
                reader = imageio.get_reader(str(video_path), format='FFMPEG')
            except Exception as e:
                print(f"Error opening {video_path.name}, skipping...", e)
                continue

            fps = reader.get_meta_data().get('fps', 60)
            fcount = 0
            fps = self.fps

            # Prepare CSV
            csv_filename = video_path.with_suffix(".csv").name
            csv_path = self.output_dir / csv_filename
            with open(csv_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['timeElapsed', 'relDist', 'isTouch', 'tapEvent'])

                rel_dist_queue = deque(maxlen=self.smooth_window)
                touch_counter = 0
                touch_state = False
                tap_event = 0
                prev_touch_state = False

                for frame in reader:
                    # print(f"Processing frame: {fcount}")
                    # imageio gives RGB frames already
                    h, w = frame.shape[:2]
                    frame = frame.astype('uint8')  # just to be safe
                    frame = np.ascontiguousarray(frame)
                    mp_frame = Image(image_format=ImageFormat.SRGB, data=frame)

                    result = hands.detect(mp_frame)

                    # display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # # # (Optional) draw landmarks
                    # if result.multi_hand_landmarks:
                    #     for lm in result.multi_hand_landmarks[0].landmark:
                    #         x, y = int(lm.x * w), int(lm.y * h)
                    #         cv2.circle(display_frame, (x, y), 3, (0, 255, 0), -1)

                    # # Show frame
                    # cv2.imshow("Debug Frame", display_frame)

                    # key = cv2.waitKey(0)

                    # # Press 'q' to quit early
                    # if key == ord('q'):
                        

                    if result.hand_landmarks:
                        hand_landmarks = result.hand_landmarks[0]

                        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                        a_pt = pts[self.FINGER_A]
                        b_pt = pts[self.FINGER_B]

                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
                        if diag < 1:
                            diag = max(w, h)

                        abs_dist = euclid(a_pt, b_pt)
                        rel_dist = abs_dist / diag

                        rel_dist_queue.append(rel_dist)
                        smooth_rel_dist = sum(rel_dist_queue) / len(rel_dist_queue)

                        is_touch = smooth_rel_dist < self.rel_touch_thresh
                        if is_touch:
                            touch_counter += 1
                        else:
                            touch_counter = 0

                        touch_state = touch_counter >= self.debounce

                        if touch_state and not prev_touch_state:
                            tap_event += 1

                        prev_touch_state = touch_state

                    else:
                        print(f"No landmarks found on frame {fcount}")
                        rel_dist_queue.clear()        
                        touch_counter = 0              
                        smooth_rel_dist = float('nan') 
                        touch_state = False

                    elapsed = fcount / fps
                    csvwriter.writerow([f"{elapsed:.5f}", f"{smooth_rel_dist:.5f}", touch_state, tap_event])
                    aggregate_csv_writer.writerow([f"{elapsed:.5f}", f"{smooth_rel_dist:.5f}", touch_state, f"{vidvals[0]}", f"{vidvals[1]}", f"{vidvals[2]}", f"{vidvals[3]}", f"{vidvals[4][0]}", tap_event])
                    fcount += 1

                print(f"Stopped on frame {fcount}")
            reader.close()
            print(f"Finished {video_path.name}, CSV saved to {csv_path.name}")
        hands.close()
        print("All tap videos processed.")
