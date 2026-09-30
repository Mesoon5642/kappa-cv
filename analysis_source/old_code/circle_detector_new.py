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
        # Determine how much to pad on each side
        pad_size = self.moving_average_window // 2
        
        # Pad the array by repeating the first and last values
        padded_arr = np.pad(arr, pad_width=pad_size, mode='edge')
        
        # Perform the convolution in 'valid' mode so it doesn't add its own zeros
        kernel = np.ones(self.moving_average_window) / self.moving_average_window
        return np.convolve(padded_arr, kernel, mode='valid')

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

        # ---- Smooth trajectory ----
        x = self.moving_average(x)
        y = self.moving_average(y)

        # ---- Velocity & acceleration ----
        dt = np.diff(t)
        dt = np.append(dt, dt[-1])
        dt[dt == 0] = 1e-8

        vx = np.gradient(x) / dt
        vy = np.gradient(y) / dt
        ax = np.gradient(vx) / dt
        ay = np.gradient(vy) / dt

        curvature = self.compute_curvature(vx, vy, ax, ay)

        # ---- Kinematic Angle Tracking (Instantaneous Heading) ----
        theta = np.arctan2(vy, vx)
        cum_theta = np.unwrap(theta)

        # ---- Instantaneous Radius (Translation Invariant) ----
        linear_speed = np.hypot(vx, vy)
        angular_velocity = np.gradient(cum_theta) / dt
        inst_r = linear_speed / (np.abs(angular_velocity) + 1e-8)

        # =====================================================================
        # PHASE LOCKING: "12 O'Clock" Detection (Max Y / Zero Crossing)
        # =====================================================================
        # Find where Vy crosses from positive (moving up) to negative (moving down).
        # This mathematically defines the apex (12 o'clock) of the curve.
        raw_crossings = np.where((vy[:-1] > 0) & (vy[1:] <= 0))[0] + 1
        
        twelve_oclocks = []
        last_t = -999.0
        
        # Debounce: Prevent noisy Vy around 0 from creating false micro-crossings
        for idx in raw_crossings:
            if (t[idx] - last_t) > (self.min_circle_duration * 0.4):
                twelve_oclocks.append(idx)
                last_t = t[idx]

        circles = []

        # =====================================================================
        # CIRCLE SEGMENTATION (Top-to-Top)
        # =====================================================================
        # By iterating exclusively between recorded 12 o'clock markers, we completely 
        # ignore the initial unreliable lead-in trajectory.
        for i in range(len(twelve_oclocks) - 1):
            start_index = twelve_oclocks[i]
            end_index = twelve_oclocks[i+1]

            duration = t[end_index] - t[start_index]
            
            if duration < self.min_circle_duration:
                continue

            # Closure/Completion check: Since we are going top-to-top, the cumulative 
            # turning angle should be ~2π. We allow an 85% tolerance for imperfect closure.
            angle_span = abs(cum_theta[end_index] - cum_theta[start_index])
            if angle_span < (self.min_rotation_radians * 0.85):
                continue

            # Check spatial closure (start point and end point should be close to each other)
            # Distance between start/end should be reasonably small to be considered "closed"
            spatial_gap = np.hypot(x[end_index] - x[start_index], y[end_index] - y[start_index])
            mean_radius = np.mean(inst_r[start_index:end_index])
            
            # If the gap is larger than 1.5x the mean radius, it's a spiral/line, not a closed circle
            if spatial_gap > (mean_radius * 1.5):
                continue

            segment_r = inst_r[start_index:end_index]
            segment_curv = curvature[start_index:end_index]
            segment_theta = cum_theta[start_index:end_index]

            # ---- Radius consistency (Using instantaneous radius) ----
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

            # If it passes the math checks, lock it in.
            if radius_ok and quadrant_ok and curvature_ok:
                circles.append([
                    t[start_index],
                    t[end_index],
                    duration,
                    start_index,
                    end_index
                ])

        # ---- Write output CSV ----
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['circleStart', 'circleEnd', 'circleDuration'])
            for c in circles:
                writer.writerow(c[:3])  # only output start, end, duration

        print(f"Detected {len(circles)} circles in file {os.path.basename(input_csv)}.")

        # ---- Plot trajectory with detected circles ----
        if self.plot_circles and len(circles) > 0:
            plt.figure(figsize=(10, 10))
            colors = cm.get_cmap('tab10', len(circles))
            
            # Plot unassigned trajectory lightly in the background to show context
            plt.plot(x, y, color='gray', alpha=0.3, linestyle='--', zorder=0)

            for idx, c in enumerate(circles):
                s_idx, e_idx = c[3], c[4]
                
                # Mark the 12 o'clock start point with a distinct scatter dot
                plt.scatter(x[s_idx], y[s_idx], color=colors(idx), marker='o', s=50, zorder=5)
                plt.plot(x[s_idx:e_idx+1], y[s_idx:e_idx+1], color=colors(idx), linewidth=2.5, label=f'Circle {idx+1}')

            plt.title(f"Detected circles in {os.path.basename(input_csv)}\n(Phase-Locked to Max Y)")
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