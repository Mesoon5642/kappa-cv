import os
import csv
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# SETTINGS
# -------------------------
# data_dir = "./slide_videos"  # directory containing CSV files
# output_dir = "./slide_videos"   # directory to save plots
# os.makedirs(output_dir, exist_ok=True)

class TapCharts:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
    def process_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # -------------------------
        # PROCESS FILES
        # -------------------------
        for filename in os.listdir(self.input_dir):
            if filename.endswith(".csv") and ("pruned" or "aggregate") not in filename:
                filepath = os.path.join(self.input_dir, filename)
                
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
                # FIND TOUCH ONSETS
                # -------------------------
                # A touch onset is True if it's True and the previous value is False
                touch_onset = np.zeros_like(is_touch, dtype=bool)
                touch_onset[0] = is_touch[0]  # handle first element
                touch_onset[1:] = is_touch[1:] & (~is_touch[:-1])

                # -------------------------
                # PLOT POSITION WITH TOUCH ONSETS
                # -------------------------
                plt.figure(figsize=(12, 6))
                plt.plot(time, rel_dist, color='blue', linewidth=2, label='Position')

                # Plot only the first True in each series
                plt.scatter(time[touch_onset], rel_dist[touch_onset], color='red', s=50, label='Touch Onset', zorder=5)

                plt.xlabel("Time (s)")
                plt.ylabel("Relative Distance")
                plt.title(filename)
                plt.grid(True)
                plt.legend()

                # Save figure
                save_name = os.path.splitext(filename)[0] + "_position.svg"
                save_path = os.path.join(self.output_dir, save_name)
                plt.savefig(save_path, format='svg')
                plt.close()

        print("All tap plots saved in:", self.output_dir)