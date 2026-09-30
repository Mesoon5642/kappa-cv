# main.py
import imageio
import mediapipe as mp
import csv
import time
import os
import sys
from config_manager import ConfigManager
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

# Config
# FINGER = 8
# FPS = 60

class CirclePositions:
    def __init__(self, input_dir, output_dir, config_path="config.json"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Load config block for this class
        cfg = ConfigManager(config_path).get_class_config("CirclePositions")

        # Preserve constructor assignment pattern
        self.finger = cfg["FINGER"]
        self.fps = cfg["FPS"]

    def process_video(self, video_path, output_csv_path):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='./model/hand_landmarker.task'),
            running_mode=RunningMode.IMAGE)
        hands = HandLandmarker.create_from_options(options)

        # Initialize imageio reader
        try:
            reader = imageio.get_reader(video_path)
        except Exception as e:
            print(f"Failed to open video {video_path}: {e}")
            return

        with open(output_csv_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['timestamp', 'relativeX', 'relativeY'])

            start_time = time.time()
            fps = self.fps
            
            # imageio allows direct iteration over the frames
            for frame_idx, frame in enumerate(reader):
                frame = frame.astype('uint8')  # just to be safe
                mp_frame = Image(image_format=ImageFormat.SRGB, data=frame)
                results = hands.detect(mp_frame)

                if results.hand_landmarks:
                    hand_landmarks = results.hand_landmarks[0]
                    finger = hand_landmarks[self.finger]   

                    relativeX = finger.x
                    relativeY = finger.y

                    timestamp = frame_idx * (1000.0 / fps)  # milliseconds as float

                    csv_writer.writerow([timestamp, relativeX, relativeY])

        reader.close()
        hands.close()
        print(f"Saved CSV: {output_csv_path}")
    
    def processs_dir(self):
        video_dir = self.input_dir
        if not os.path.isdir(video_dir):
            print(f"{video_dir} is not a valid directory")
            sys.exit(1)

        # Process all video files in the directory
        for file_name in os.listdir(video_dir):
            if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                video_path = os.path.join(video_dir, file_name)
                csv_name = os.path.splitext(file_name)[0] + '.csv'
                csv_path = os.path.join(self.output_dir, csv_name)
                self.process_video(video_path, csv_path)