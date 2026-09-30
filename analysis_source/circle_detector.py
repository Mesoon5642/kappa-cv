import numpy as np
import csv
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from config_manager import ConfigManager

# # -----------------------------
# # GLOBAL CONSTANTS / PARAMETERS
# # -----------------------------
# SMOOTHING_WINDOW = 5
# RADIUS_VARIATION_THRESH = 0.75
# CURVATURE_SMOOTHNESS_THRESH = 5.0
# MIN_ROTATION_RADIANS = 2 * np.pi
# MIN_CIRCLE_DURATION = 0.5
# MOVING_AVERAGE_WINDOW = 5
# REQUIRE_QUADRANTS = True
# PLOT_CIRCLES = True
# -----------------------------

class CircleDetector:
    def __init__(self, input_dir, output_dir, config_path="config.json"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Load config block for this class
        cfg = ConfigManager(config_path).get_class_config("CircleDetector")

        # Preserve constructor assignment pattern
        self.radius_var_thresh = cfg["RADIUS_VARIATION_THRESH"]
        self.curv_smooth_thresh = cfg["CURVATURE_SMOOTHNESS_THRESH"]
        self.min_rotation_radians = cfg["MIN_ROTATION_RADIANS"]
        self.min_circle_duration = cfg["MIN_CIRCLE_DURATION"]
        self.require_quadrants = cfg["REQUIRE_QUADRANTS"]
        self.moving_average_window = cfg["MOVING_AVERAGE_WINDOW"]
        self.plot_circles = cfg["PLOT_CIRCLES"]
    
    def moving_average(self, arr):
        kernel = np.ones(self.moving_average_window) / self.moving_average_window
        return np.convolve(arr, kernel, mode='same')


    def compute_curvature(self, vx, vy, ax, ay):
        numerator = np.abs(vx * ay - vy * ax)
        denominator = (vx**2 + vy**2)**1.5
        denominator[denominator == 0] = 1e-8
        return numerator / denominator


    def detect_circles_file(self, input_csv, output_csv, circle_plot_name):

        # ---- Load CSV ----
        t, x, y = [], [], []

        with open(input_csv, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t.append(float(row['timestamp']) / 1000.0)
                x.append(float(row['relativeX']))
                y.append(float(row['relativeY']))

        t = np.array(t)
        x = np.array(x)
        y = np.array(y)
        # x = -x

        # ---- Smooth trajectory ----
        x = self.moving_average(x)
        y = self.moving_average(y)

        # ---- Fixed global center ----
        cx = np.mean(x)
        cy = np.mean(y)

        y = -y + 2 * cy

        # ---- Angle tracking ----
        # theta = np.arctan2(y - cy, x - cx)
        # theta = np.unwrap(theta)

        # ---- Velocity & acceleration ----
        dt = np.diff(t)
        dt = np.append(dt, dt[-1])
        dt[dt == 0] = 1e-8

        vx = np.gradient(x) / dt
        vy = np.gradient(y) / dt
        ax = np.gradient(vx) / dt
        ay = np.gradient(vy) / dt

        curvature = self.compute_curvature(vx, vy, ax, ay)

        # ---- Radius from fixed center ----
        r = np.sqrt((x - cx)**2 + (y - cy)**2)

        circles = []
        start_index = 0

        for i in range(1, len(x)):

            seg_theta = np.arctan2(y[start_index:i+1] - cy,
                        x[start_index:i+1] - cx)
            seg_theta = np.unwrap(seg_theta)

            angle_span = seg_theta[-1] - seg_theta[0]

            if abs(angle_span) >= self.min_rotation_radians:

                end_index = i
                duration = t[end_index] - t[start_index]

                if duration < self.min_circle_duration:
                    start_index = i
                    continue

                segment_r = r[start_index:end_index]
                segment_curv = curvature[start_index:end_index]
                segment_theta = seg_theta

                # ---- Radius consistency ----
                radius_ok = (np.std(segment_r) / (np.mean(segment_r) + 1e-8)) < self.radius_var_thresh

                # ---- Quadrant coverage ----
                if self.require_quadrants:
                    angles = (segment_theta - segment_theta[0]) % (2 * np.pi)
                    visited = [
                        np.any((angles >= 0) & (angles < np.pi / 2)),
                        np.any((angles >= np.pi / 2) & (angles < np.pi)),
                        np.any((angles >= np.pi) & (angles < 3 * np.pi / 2)),
                        np.any((angles >= 3 * np.pi / 2) & (angles < 2 * np.pi))
                    ]
                    quadrant_ok = all(visited)
                else:
                    quadrant_ok = True

                # ---- Curvature smoothness ----
                curvature_ok = (
                    np.std(segment_curv) < self.curv_smooth_thresh * (np.mean(segment_curv) + 1e-8)
                )

                if radius_ok and quadrant_ok and curvature_ok:
                    circles.append([
                        t[start_index],
                        t[end_index],
                        duration,
                        start_index,
                        end_index
                    ])

                start_index = i

        # ---- Write output CSV ----
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['circleStart', 'circleEnd', 'circleDuration'])
            for c in circles:
                writer.writerow(c[:3])  # only output start, end, duration

        print(f"Detected {len(circles)} circles in file {input_csv}.")

        # ---- Plot trajectory with detected circles ----
        if self.plot_circles and len(circles) > 0:
            plt.figure(figsize=(10, 10))
            colors = cm.get_cmap('tab10', len(circles))
            for idx, c in enumerate(circles):
                s_idx, e_idx = c[3], c[4]
                plt.scatter(x[s_idx], y[s_idx], color=colors(idx), marker='o', s=50)
                plt.plot(x[s_idx:e_idx+1], y[s_idx:e_idx+1], color=colors(idx), linewidth=2, label=f'Circle {idx+1}')

            plt.scatter(cx, cy, color='black', marker='x', label='Estimated Center')
            plt.title(f"Detected circles in {os.path.basename(input_csv)}")
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.legend()
            plt.tight_layout()
            plt.savefig(circle_plot_name, dpi=300, bbox_inches='tight', format='svg')
            plt.close()


    def process_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        csv_files = glob.glob(os.path.join(self.input_dir, "*.csv"))

        for csv_file in csv_files:
            if "_circles.csv" in csv_file:
                continue
            base_name = os.path.basename(csv_file)
            name_no_ext = os.path.splitext(base_name)[0]
            output_csv = os.path.join(self.output_dir, f"{name_no_ext}_circles.csv")
            output_graph = os.path.join(self.output_dir, f"{name_no_ext}_circles.svg")
            self.detect_circles_file(csv_file, output_csv, output_graph)