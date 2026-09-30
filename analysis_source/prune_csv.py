import csv
import os
import numpy as np
import librosa
from scipy.io import wavfile
from scipy.signal import find_peaks
from config_manager import ConfigManager


class TapCSVPrune:
    def __init__(self, input_dir, output_dir, config_path="config.json"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        cfg = ConfigManager(config_path).get_class_config("TapCSVPrune")

        # Existing config
        self.prune_start = cfg["PRUNE_START"]
        self.prune_end = cfg["PRUNE_END"]
        self.max_taps_per_sec = cfg["MAX_TAPS_PER_SEC"]
        self.min_taps_per_sec = cfg["MIN_TAPS_PER_SEC"]
        self.window_size = cfg["WINDOW_SIZE"]

        # New config
        self.min_tap_length = cfg["MIN_TAP_LENGTH"]
        self.bpm = cfg["BPM"]
        self.raw_audio = cfg["RAW_AUDIO"]
        self.drop_excessive_taps = cfg["DROP_EXCESSIVE_TAPS"]
        self.fix_slow_taps = cfg["FIX_SLOW_TAPS"]

    def detect_taps(self, time, dist, touch):
        taps = []
        i = 0
        n = len(touch)

        while i < n:
            if touch[i]:
                start = i
                while i < n and touch[i]:
                    i += 1
                end = i - 1

                taps.append({
                    "start_idx": start,
                    "end_idx": end,
                    "start_time": time[start],
                    "end_time": time[end],
                    "distances": dist[start:end + 1]
                })
            else:
                i += 1

        return taps

    def prune_and_flag_taps(self, taps):
        if not taps:
            return None, False, True  # no data → unresolved

        tap_stats = []
        tap_starts = []

        for tap in taps:
            duration = tap["end_time"] - tap["start_time"]
            tap_stats.append([
                tap["start_time"],
                tap["end_time"],
                duration,
                np.min(tap["distances"]),
                np.max(tap["distances"]),
                np.mean(tap["distances"])
            ])
            tap_starts.append(tap["start_time"])

        tap_stats = np.array(tap_stats)
        tap_starts = np.array(tap_starts)

        # Start/end prune
        end_idx = len(tap_stats) - self.prune_end
        tap_stats = tap_stats[self.prune_start:end_idx]
        tap_starts = tap_starts[self.prune_start:end_idx]

        durations = tap_stats[:, 2]
        length_mask = durations >= self.min_tap_length

        had_issue = not np.all(length_mask)
        unresolved = False  # pruning fixes it

        tap_stats = tap_stats[length_mask]
        tap_starts = tap_starts[length_mask]

        if len(tap_stats) == 0:
            return None, True, True

        start_matrix = tap_starts[:, None]
        counts = ((tap_starts >= start_matrix) &
                  (tap_starts < start_matrix + self.window_size)).sum(axis=1)

        rate_flag = (counts > self.max_taps_per_sec) | (counts < self.min_taps_per_sec)

        if np.any(rate_flag):
            had_issue = True
            unresolved = True  # no fix exists

        tap_stats = np.column_stack([tap_stats, rate_flag])

        return tap_stats, had_issue, unresolved

    def get_audio_events(self, time, csv_path):
        if self.raw_audio:
            return self.extract_audio_events(csv_path)
        else:
            interval = 60.0 / self.bpm
            return np.arange(time[0], time[-1], interval)

    def extract_audio_events(self, csv_path):
        # Convert CSV path → video path
        video_path = os.path.splitext(csv_path)[0] + ".webm"

        if not os.path.exists(video_path):
            print(f"Video not found for audio extraction: {video_path}")
            return np.array([])

        try:
            # librosa loads directly from video (via ffmpeg backend)
            audio, sr = librosa.load(video_path, sr=None, mono=True)
        except Exception as e:
            print(f"Audio load failed: {e}")
            return np.array([])

        # Envelope (same logic, just cleaner)
        envelope = np.abs(audio)

        # Normalize safely
        max_val = np.max(envelope)
        if max_val > 0:
            envelope = envelope / max_val

        # Peak detection
        peaks, _ = find_peaks(
            envelope,
            height=0.5,              
            distance=int(sr * 0.3)   
        )

        print("Finished extracting audio directly from video")

        return peaks / sr

    def align_events(self, tap_starts, audio_events):
        t_i, a_i = 0, 0
        aligned_taps = []
        aligned_audio = []

        had_issue = False
        unresolved = False

        while t_i < len(tap_starts) and a_i < len(audio_events):
            tap = tap_starts[t_i]
            audio = audio_events[a_i]

            if abs(tap - audio) <= self.window_size:
                aligned_taps.append(tap)
                aligned_audio.append(audio)
                t_i += 1
                a_i += 1

            elif tap < audio:
                had_issue = True
                if self.drop_excessive_taps:
                    t_i += 1  # fixed
                else:
                    unresolved = True
                    t_i += 1

            else:
                had_issue = True
                if self.fix_slow_taps:
                    a_i += 1  # fixed
                else:
                    unresolved = True
                    a_i += 1

        return np.array(aligned_taps), np.array(aligned_audio), had_issue, unresolved

    def check_event_mismatch(self, tap_events, audio_count):
        expected = np.arange(audio_count)
        length = min(len(tap_events), len(expected))

        if length == 0:
            return True

        diffs = np.abs(tap_events[:length] - expected[:length])
        return np.any(diffs > 1)

    def process_csv(self, path):
        data = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")

        time = data["timeElapsed"].astype(float)
        dist = data["relDist"].astype(float)
        touch = data["isTouch"].astype(bool)
        tap_event = data["tapEvent"].astype(int)

        taps = self.detect_taps(time, dist, touch)

        tap_stats, _, unresolved_prune = self.prune_and_flag_taps(taps)

        if tap_stats is None or len(tap_stats) == 0:
            return None, True

        tap_starts = tap_stats[:, 0]

        audio_events = self.get_audio_events(time, path)

        aligned_taps, aligned_audio, _, unresolved_align = self.align_events(
            tap_starts, audio_events
        )

        mismatch = self.check_event_mismatch(tap_event, len(aligned_audio))

        if mismatch:
            if not (self.drop_excessive_taps or self.fix_slow_taps):
                unresolved_mismatch = True
            else:
                unresolved_mismatch = False
        else:
            unresolved_mismatch = False

        unresolved_issue = (
            unresolved_prune or
            unresolved_align or
            unresolved_mismatch
        )

        count_mismatch = len(aligned_taps) != len(aligned_audio)

        if count_mismatch:
            # If we had the ability to fix but still failed, unresolved
            if self.drop_excessive_taps or self.fix_slow_taps:
                unresolved_issue = True
            else:
                # If fixes are disabled, ALWAYS flag
                unresolved_issue = True
        
        flagged = unresolved_issue

        return tap_stats, flagged

    def batch_prune(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for fname in os.listdir(self.input_dir):
            if not fname.endswith(".csv") or \
               fname.lower().count("audio") >= 2 or \
               "aggregate" in fname or \
               "pruned" in fname:
                continue

            print(f"processing {fname}")

            in_path = os.path.join(self.input_dir, fname)
            tap_stats, flagged = self.process_csv(in_path)

            if tap_stats is None or len(tap_stats) == 0:
                print(f"No valid taps in {fname}")
                continue

            base, ext = os.path.splitext(fname)
            out_name = f"{base}_pruned"

            if flagged:
                out_name += "_flagged"

            out_name += ext
            out_path = os.path.join(self.output_dir, out_name)

            with open(out_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "tapStart",
                    "tapEnd",
                    "tapDuration",
                    "minDist",
                    "maxDist",
                    "avgDist",
                    "isFlag"
                ])
                writer.writerows(tap_stats)

            print(f"Saved: {out_path}")