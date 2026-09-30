import csv
import os
import numpy as np
from config_manager import ConfigManager

PRUNE_START = 0
PRUNE_END = 0
MIN_TAP_FRAMES = 50
MAX_TAPS_PER_SEC = 3
MIN_TAPS_PER_SEC = 1
WINDOW_SIZE = 1.0  # seconds

class TapCSVPrune:
    def __init__(self, input_dir, output_dir, config_path="config.json"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Load config block for this class
        cfg = ConfigManager(config_path).get_class_config("TapCSVPrune")

        # Preserve constructor assignment pattern
        self.prune_start = cfg["PRUNE_START"]
        self.prune_end = cfg["PRUNE_END"]
        self.min_tap_frames = cfg["MIN_TAP_FRAMES"]
        self.max_taps_per_sec = cfg["MAX_TAPS_PER_SEC"]
        self.min_taps_per_sec = cfg["MIN_TAPS_PER_SEC"]
        self.window_size = cfg["WINDOW_SIZE"]
        
    def detect_taps(self, time, dist, touch):
        """Detect all contiguous True groups as raw taps."""
        n = len(touch)
        taps = []
        i = 0
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
                    "distances": dist[start:end+1]
                })
            else:
                i += 1
        return taps

    def prune_and_flag_taps(self, taps):
        """Prune short taps and compute per-tap stats."""
        if not taps:
            return None, False

        # Compute stats for each tap
        tap_stats = []
        tap_starts = []
        for tap in taps:
            duration = tap["end_time"] - tap["start_time"]
            min_d = np.min(tap["distances"])
            max_d = np.max(tap["distances"])
            avg_d = np.mean(tap["distances"])
            tap_stats.append([tap["start_time"], tap["end_time"], duration, min_d, max_d, avg_d])
            tap_starts.append(tap["start_time"])

        tap_stats = np.array(tap_stats)
        tap_starts = np.array(tap_starts)

        # Prune
        taps_end_prune = len(tap_starts) - self.prune_end
        tap_stats = tap_stats[self.prune_start:taps_end_prune]
        tap_starts = tap_starts[self.prune_start:taps_end_prune]

        # Vectorized tap-rate check (per tap)
        start_matrix = tap_starts[:, None]
        counts = ((tap_starts >= start_matrix) & (tap_starts < start_matrix + self.window_size)).sum(axis=1)
        is_flag = (counts > self.max_taps_per_sec) | (counts < self.min_taps_per_sec)

        any_flagged = np.any(is_flag)

        # Prune taps shorter than MIN_TAP_FRAMES
        frame_counts = np.array([tap["end_idx"] - tap["start_idx"] + 1 for tap in taps])
        mask = frame_counts >= self.min_tap_frames
        any_flagged = any_flagged or not np.all(mask)  # if any tap removed due to short length, flag the file

        # Append isFlag column
        tap_stats = np.column_stack([tap_stats, is_flag])

        return tap_stats, any_flagged

    def process_csv(self, path):
        data = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")
        time = data["timeElapsed"].astype(float)
        dist = data["relDist"].astype(float)
        touch = np.array([x == True for x in data["isTouch"]], dtype=bool)

        taps = self.detect_taps(time, dist, touch)
        tap_stats, flagged = self.prune_and_flag_taps(taps)
        return tap_stats, flagged

    def batch_prune(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for fname in os.listdir(self.input_dir):
            if not fname.endswith(".csv") or fname.lower().count("audio") >= 2 or "aggregate" in fname:
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