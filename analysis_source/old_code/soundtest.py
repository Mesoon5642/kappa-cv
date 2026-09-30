import os
import csv
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# SETTINGS
# -------------------------
data_dir = "./slide_videos"  # directory containing CSV files
output_dir = "./slide_videos"   # directory to save plots
os.makedirs(output_dir, exist_ok=True)

# -------------------------
# PROCESS FILES
# -------------------------
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        filepath = os.path.join(data_dir, filename)
        
        # -------------------------
        # LOAD CSV DATA
        # -------------------------
        time = []
        rel_dist = []
        is_touch = []

        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0].lower() == 'timeelapsed':  # skip header
                    continue
                time.append(float(row[0]))
                rel_dist.append(float(row[1]))
                is_touch.append(row[2] == 'True')

        time = np.array(time)
        rel_dist = np.array(rel_dist)
        is_touch = np.array(is_touch)

        # -------------------------
        # PLOT CONTIGUOUS LINE WITH COLOR
        # -------------------------
        plt.figure(figsize=(12, 6))

        # Make two masked arrays for touch and no-touch
        no_touch_y = np.ma.masked_where(is_touch, rel_dist)
        touch_y = np.ma.masked_where(~is_touch, rel_dist)

        plt.plot(time, no_touch_y, color='red', linewidth=2, label='No Touch')
        plt.plot(time, touch_y, color='green', linewidth=2, label='Touch')

        plt.xlabel("Time (s)")
        plt.ylabel("Relative Distance")
        plt.title(filename)
        plt.grid(True)
        plt.legend()

        # Save figure
        save_name = os.path.splitext(filename)[0] + "_taps.svg"
        save_path = os.path.join(output_dir, save_name)
        plt.savefig(save_path, format='svg')
        plt.close()

print("All plots saved in:", output_dir)