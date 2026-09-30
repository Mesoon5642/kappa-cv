import csv
import numpy as np
import matplotlib.pyplot as plt
import librosa
from scipy.signal import find_peaks
import subprocess
import os

class CircleDrift:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
    # -----------------------------
    # AUDIO PROCESSING
    # -----------------------------
    def extract_audio(self, video_path, wav_path):
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-ac", "1",
            "-ar", "48000",
            wav_path
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def detect_click_beats(self, wav_path):
        y, sr = librosa.load(wav_path, sr=None)

        # amplitude envelope
        envelope = np.abs(y)

        # normalize
        envelope = envelope / np.max(envelope)

        # detect peaks
        peaks, _ = find_peaks(
            envelope,
            height=0.5,
            distance=int(sr * 0.3)  # minimum spacing between beats
        )

        beat_times = peaks / sr
        return beat_times


    def get_beats_from_video(self, video_path):
        wav_path = video_path.replace(".webm", "_temp.wav")

        self.extract_audio(video_path, wav_path)

        if not os.path.exists(wav_path):
            print(f"Audio extraction failed for {video_path}")

        beat_times = self.detect_click_beats(wav_path)

        os.remove(wav_path)

        if len(beat_times) < 2:
            print(f"Not enough beats detected in {video_path}")

        interval = np.median(np.diff(beat_times))
        return beat_times, interval


    # -----------------------------
    # LOAD TAP DATA (UPDATED)
    # -----------------------------
    def load_taps(self, csv_path):
        taps = []
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    taps.append(float(row["circleStart"]))
                except (ValueError, KeyError):
                    continue
        return np.array(taps)


    # -----------------------------
    # COMPUTE PHASES + OFFSETS
    # -----------------------------
    def compute_phases_and_offsets(self, tap_times, beat_times, interval):
        phases = []
        offsets = []
        half_T = interval / 2.0

        for i in range(len(beat_times)):
            if i >= len(tap_times):
                break

            idx = np.argmin(np.abs(beat_times - tap_times[i]))
            closest = beat_times[idx]
            offset = tap_times[i] - closest

            # wrap to [-T/2, T/2]
            if offset > half_T:
                offset -= interval
            elif offset < -half_T:
                offset += interval

            phase = -2 * np.pi * (offset / interval)

            phases.append(phase)
            offsets.append(offset)

        return np.array(phases), np.array(offsets)


    # -----------------------------
    # CIRCULAR STATISTICS
    # -----------------------------
    def circular_stats(self, phases):
        x = np.cos(phases)
        y = np.sin(phases)

        mean_angle = np.arctan2(np.mean(y), np.mean(x))
        R = np.sqrt(np.mean(x)**2 + np.mean(y)**2)
        circ_std = np.sqrt(-2 * np.log(R))

        return mean_angle, R, circ_std


    # -----------------------------
    # PLOT CIRCULAR GRAPH
    # -----------------------------
    def plot_circle(self, phases, mean_angle, offsets, R, circ_std,
                    title, save_path):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')

        ax.set_theta_zero_location("E")
        ax.set_theta_direction(1)

        # Perfect timing line
        ax.plot([0, np.pi], [1, 1], linewidth=2)

        # Taps
        ax.scatter(phases, np.ones_like(phases), s=60)

        # Mean vector
        ax.plot([mean_angle, mean_angle], [0, R], linewidth=3)

        ax.set_yticklabels([])

        # Title
        ax.set_title(title, fontsize=12, pad=20)

        # Stats box
        stats_text = (
            f"Circular R: {R:.3f}\n"
            f"Circular Std: {circ_std:.3f}\n"
            f"Mean Angle: {mean_angle:.3f} rad\n"
            f"\n"
            f"Offsets:\n"
            f"Mean: {np.mean(offsets):.3f}\n"
            f"Median: {np.median(offsets):.3f}\n"
            f"Std: {np.std(offsets):.3f}\n"
        )

        plt.figtext(0.02, 0.02, stats_text, fontsize=10)

        plt.savefig(save_path, dpi=300, bbox_inches='tight', format='svg')
        plt.close(fig)


    # -----------------------------
    # MAIN
    # -----------------------------
    def processs_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for filename in os.listdir(self.input_dir):

            if not filename.endswith(".csv"):
                continue

            if "noAudio" in filename:
                print("Skipping (no audio):", filename)
                continue

            csv_path = os.path.join(self.input_dir, filename)

            # UPDATED: new naming convention
            base = filename.replace("_circles.csv", "")

            video_name = base + ".webm"
            video_path = os.path.join(self.input_dir, video_name)

            if not os.path.exists(video_path):
                print("Video not found:", video_name)
                continue

            tap_times = self.load_taps(csv_path)

            beat_times, interval = self.get_beats_from_video(video_path)

            if (len(beat_times) < len(tap_times)):
                continue

            print(f"Tap Times: {tap_times}")
            print(f"Beat Times: {beat_times}")

            phases, offsets = self.compute_phases_and_offsets(
                tap_times, beat_times, interval
            )

            print("Offsets:", offsets)

            mean_angle, R, circ_std = self.circular_stats(phases)

            print("Processing:", filename)
            print("  R =", R)
            print("")

            output_name = filename.replace(".csv", "_circular.svg")
            save_path = os.path.join(self.output_dir, output_name)

            self.plot_circle(
                phases,
                mean_angle,
                offsets,
                R,
                circ_std,
                title=filename.replace(".csv", ""),
                save_path=save_path
            )

        print("All files processed.")