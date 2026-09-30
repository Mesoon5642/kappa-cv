from tap_positions import TapPositions
from tap_drift import TapDrift
from tap_charts import TapCharts
from prune_csv import TapCSVPrune
from circle_positions import CirclePositions
from circle_detector import CircleDetector
from circle_drift import CircleDrift

class AnalysisDriver:
    # Each part of the pipeline has 3 lines:
    # Class definition, Class Function, Print Statement
    # Comment out all three if you want to "remove" a part of the pipeline
    # For example:
    # tp = TapPositions(input_dir, output_dir, first_run)
    # tp.process_directory()
    # print("Finished Tap Positions")
    def proces_taps(self, input_dir, output_dir, first_run):
        tp = TapPositions(input_dir, output_dir, first_run)
        tp.process_directory()
        print("Finished Tap Positions")
        tpcsv = TapCSVPrune(input_dir, output_dir)
        tpcsv.batch_prune()
        print("Finished Pruning")
        td = TapDrift(input_dir, output_dir)
        td.process_directory()
        print("Finished Tap Drift")
        tc = TapCharts(input_dir, output_dir)
        tc.process_directory()
        print(f"All processes for taps, find your output in {output_dir}")
    def process_circles(self, input_dir, output_dir):
        circle_pos = CirclePositions(input_dir, output_dir)
        circle_pos.processs_dir()
        print("Finished circle positions")
        cdet = CircleDetector(input_dir, output_dir)
        cdet.process_directory()
        print("Finished circle detection")
        cdrift = CircleDrift(input_dir, output_dir)
        cdrift.processs_directory()
        print(f"All processes for circles, find your output in {output_dir}")

if __name__ == "__main__":
    ad = AnalysisDriver()
    # Important functions. params are (input_folder, output_folder, firstRun)
    # firstRun re-encodes tap videos if the detector is having issues. 
    # TODO: Implement re-encoding for circles if needed

    # Comment out either of these functions if you don't want to run them
    # "#" is the comment character in python
    ad.proces_taps("./slide_videos_tap", "./slide_videos_tap", False)
    ad.process_circles("./slide_videos_circles", "./slide_videos_circles")