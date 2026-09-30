import csv
import numpy as np
import matplotlib.pyplot as plt
from config_manager import ConfigManager
import librosa
from scipy.signal import find_peaks
import subprocess
import os


class TapDrift:
    def __init__(self, input_dir, output_dir, config_path="config.json"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        cfg = ConfigManager(config_path).get_class_config("TapCSVPrune")
        self.RAW_AUDIO = cfg["RAW_AUDIO"]
        self.BPM = cfg["BPM"]

    # -----------------------------
    # AUDIO EXTRACTION
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

    # -----------------------------
    # RAW AUDIO BEAT DETECTION
    # -----------------------------
    def detect_click_beats(self, wav_path):
        y, sr = librosa.load(wav_path, sr=None)

        envelope = np.abs(y)
        envelope = envelope / np.max(envelope)

        peaks, _ = find_peaks(
            envelope,
            height=0.5,
            distance=int(sr * 0.3)
        )

        beat_times = peaks / sr
        return beat_times

    # -----------------------------
    # UNIFIED BEAT GENERATION
    # -----------------------------
    def get_beats_from_video(self, video_path):

        # ==========================================================
        # MODE 1: RAW AUDIO (UNCHANGED BEHAVIOR)
        # ==========================================================
        if self.RAW_AUDIO:
            wav_path = video_path.replace(".webm", "_temp.wav")

            self.extract_audio(video_path, wav_path)

            if not os.path.exists(wav_path):
                raise RuntimeError(f"Audio extraction failed for {video_path}")

            beat_times = self.detect_click_beats(wav_path)

            os.remove(wav_path)

            interval = np.median(np.diff(beat_times))
            return beat_times, interval

        # ==========================================================
        # MODE 2: BPM-BASED SYNTHETIC BEATS
        # ==========================================================
        else:
            # infer timing purely from BPM
            interval = 60.0 / self.BPM

            # create synthetic beat grid over video duration
            # (we approximate duration from file metadata via librosa)
            y, sr = librosa.load(video_path, sr=None, mono=True)
            duration = len(y) / sr

            beat_times = np.arange(0, duration, interval)

            return beat_times, interval

    # -----------------------------
    # LOAD TAPS
    # -----------------------------
    def load_taps(self, csv_path):
        taps = []
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                taps.append(float(row["tapStart"]))
        return np.array(taps)

    # -----------------------------
    # PHASES + OFFSETS
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

            if offset > half_T:
                offset -= interval
            elif offset < -half_T:
                offset += interval

            phase = -2 * np.pi * (offset / interval)

            phases.append(phase)
            offsets.append(offset)

        return np.array(phases), np.array(offsets)

    # -----------------------------
    # CIRCULAR STATS
    # -----------------------------
    def circular_stats(self, phases):
        x = np.cos(phases)
        y = np.sin(phases)

        mean_angle = np.arctan2(np.mean(y), np.mean(x))
        R = np.sqrt(np.mean(x)**2 + np.mean(y)**2)
        circ_std = np.sqrt(-2 * np.log(R))

        return mean_angle, R, circ_std

    # -----------------------------
    # PLOT
    # -----------------------------
    def plot_circle(self, phases, mean_angle, offsets, R, circ_std,
                    title, save_path):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')

        ax.set_theta_zero_location("E")
        ax.set_theta_direction(1)

        ax.plot([0, np.pi], [1, 1], linewidth=2)
        ax.scatter(phases, np.ones_like(phases), s=60)
        ax.plot([mean_angle, mean_angle], [0, R], linewidth=3)

        ax.set_yticklabels([])
        ax.set_title(title, fontsize=12, pad=20)

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
    # MAIN PIPELINE
    # -----------------------------
    def process_directory(self):

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for filename in os.listdir(self.input_dir):

            if not filename.endswith(".csv") or "aggregate" in filename or "pruned" not in filename:
                continue

            if "noAudio" in filename:
                print("Skipping (no audio):", filename)
                continue

            csv_path = os.path.join(self.input_dir, filename)

            base = filename.replace("_pruned_flagged.csv", "")
            base = base.replace("_pruned.csv", "")

            video_name = base + ".webm"
            video_path = os.path.join(self.input_dir, video_name)

            if not os.path.exists(video_path):
                print("Video not found:", video_name)
                continue

            tap_times = self.load_taps(csv_path)
            beat_times, interval = self.get_beats_from_video(video_path)

            print(f"Tap Times: {tap_times}")
            print(f"Beat Times: {beat_times}")

            phases, offsets = self.compute_phases_and_offsets(
                tap_times, beat_times, interval
            )

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

        print("All drift files processed.")