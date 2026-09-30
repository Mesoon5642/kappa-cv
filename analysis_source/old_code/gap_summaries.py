import csv
import statistics
import os
import sys

class CSV_Summary:
    def __init__(self) -> None:
        self.csv_stats_list = {}
        self.global_stats = None

    def read_all_csvs(self, folderpath) -> None:
        """Read all CSV files and compute ITIs based on tapStart"""
        for entry in os.listdir(folderpath):
            if entry.endswith(".csv") and entry.lower().count("audio") < 2:
                fullpath = os.path.join(folderpath, entry)
                with open(fullpath, mode='r') as file:
                    fs = csv.DictReader(file)
                    tap_starts = []
                    for row in fs:
                        try:
                            tap_starts.append(float(row["tapStart"]))
                        except ValueError:
                            continue  # skip invalid rows

                    # Compute ITI intervals and lengths
                    intervals = []
                    interval_lens = []
                    if len(tap_starts) > 0:
                        # First ITI = time before first tap
                        intervals.append([0.0, tap_starts[0]])
                        interval_lens.append(tap_starts[0])
                        # Remaining ITIs
                        for i in range(1, len(tap_starts)):
                            intervals.append([tap_starts[i-1], tap_starts[i]])
                            interval_lens.append(tap_starts[i] - tap_starts[i-1])

                    self.csv_stats_list[entry] = CSV_File_Stats(entry, intervals, interval_lens)

    def calculate_global_stats(self, doReadout):
        if len(self.csv_stats_list) < 1:
            print("Run \"read_all_csvs\" function first before running summary functions!")
            return

        global_lens = []
        global_intervals = []
        for csv_file in self.csv_stats_list.values():
            global_intervals.extend(csv_file.iti_intervals)
            global_lens.extend(csv_file.iti_interval_lens)

        self.global_stats = CSV_File_Stats("global", global_intervals, global_lens)

        if doReadout:
            self.readout_global_stats()

    def readout_individual_stats(self, filename) -> None:
        if len(self.csv_stats_list) < 1:
            print("Run \"read_all_csvs\" function first before running summary functions!")
            return
        if filename not in self.csv_stats_list:
            print("Filename not found in summary list")
            return
        self.csv_stats_list[filename].stats_readout()

    def readout_global_stats(self):
        if isinstance(self.global_stats, CSV_File_Stats):
            self.global_stats.stats_readout()
        else:
            print("No global stats object found! Run \"calculate_global_stats\" function!")

    def readout_all_stats(self):
        self.calculate_global_stats(False)
        for csv_file in self.csv_stats_list.values():
            csv_file.stats_readout()
        self.readout_global_stats()


class CSV_File_Stats:
    def __init__(self, filename, iti_intervals, iti_interval_lens):
        self.filename = filename
        self.iti_intervals = iti_intervals
        self.iti_interval_lens = iti_interval_lens
        self.num_itis = len(self.iti_interval_lens)

        # Handle case with 0 or 1 ITI
        if self.num_itis > 0:
            self.mean_interval = statistics.mean(self.iti_interval_lens)
            self.med_interval = statistics.median(self.iti_interval_lens)
            self.shortest_iti = min(self.iti_interval_lens)
            self.longest_iti = max(self.iti_interval_lens)
        else:
            self.mean_interval = self.med_interval = 0
            self.shortest_iti = self.longest_iti = 0

        if self.num_itis > 1:
            self.sd_interval = statistics.stdev(self.iti_interval_lens)
            self.var_interval = statistics.variance(self.iti_interval_lens)
        else:
            self.sd_interval = self.var_interval = 0

    def stats_readout(self):
        if self.filename == "global":
            print(f"Statistics Across All Files:\n")
        else:
            print(f"Statistics for {self.filename}:\n")
        print(f"Total Number of ITIs: {self.num_itis}")
        print(f"Mean ITI Length (sec): {self.mean_interval}")
        print(f"Median ITI Length (sec): {self.med_interval}")
        print(f"Standard Deviation of ITI Lengths (sec): {self.sd_interval}")
        print(f"Variance of ITI Lengths (sec): {self.var_interval}")
        print(f"Shortest ITI (sec): {self.shortest_iti}")
        print(f"Longest ITI (sec): {self.longest_iti}")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python soundtest_summary.py <csv_directory>")
        sys.exit(1)

    csv_stats = CSV_Summary()
    csv_stats.read_all_csvs(sys.argv[1])
    csv_stats.readout_all_stats()
