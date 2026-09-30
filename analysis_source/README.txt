INSTRUCTIONS HERE:

SETUP BEFORE RUNNING:

1. Install Python (already done on the lab computer)
2. Open the "analysis_source" directory in some form of terminal.
    TIP: One easy way to do this is to right click in a given folder
    in file explorer, and click the "Open in Terminal" option. No "cd" required!
3. Run the command "python -m venv env". This sets up the virtual environment
4. Once the command has completed, run "pip install -r requirements.txt". 
This will install needed Python packages
5. Congrats, you've (hopefully) configred packages/setup correctly!

RUNNING THE PROGRAM:

Use the command "python analysis_driver.py" (or replace python with py if you're having issues)
Make sure to read the comments in analysis_driver.py on how to run certain parts of the pipeline individually,
as well as what arguments to pass. Set input and output directory correctly!

It is advised that you have your input/output dirs in the same directory as the code.
It makes filepaths easier to input! Note that the existing input/output dir parameters
are based off of directories located in the same directory as code, ;)

PIPELINES:

Tap:
Position Data/Aggregation -> Tap Pruning -> Tap Phase Detection/Frequency Charts

Circle:
Position Data -> Circle Detection -> Circular Phase Detection

CONFIG VARIABLES (located in config.json):

TapPositions:

Finger_A/Finger_B: The two finger indexes used for detecting taps. See mediapipe's
hand model documentation for what each index is
Relative_Touch_Threshold: How close the two fingers must be to detect a tap.
0.15 is a good default, lower is more strict, higher is less strict (0->1)
Debounce_Frames: How many frames the program will wait before detecting another tap. Set to 1 to ignore
Smoothing Window: The smoothing window for distance calculations. Set to 1 to ignore
FPS: The FPS of the input video. MAKE SURE THIS MATCHES (should default to 60)

TapCSVPrune:

Prune_Start/Prune_End: How many tap events to remove from further analysis.
Measured as "x taps removed from the start/end"
Max_Taps_Per_Sec: Maximum number of taps that can happen in between two audio thresholds. Mostly depreciated
Min_Taps_Per_Sec: Minimum number of taps that can happen in between two audio thresholds. Mostly depreciated.
Window Size: The window for max/min taps in seconds. 
Yes, naming is confusing, but these three are mostly depreciated. Leave to defaults, ideally
Min_Tap_Length: Minimum tap length in real time, in seconds
BPM: BPM used for inferring audio timing
Raw_Audio: Whether or not to use the "raw audio feed" to determine audio onsets.
If true, will analyze the video's audio to determine onset times
If false, will infer audio onsets based on BPM config value
Drop_Excessive_Taps: Whether or not to drop excessive taps automatically between two audio onsets
Fix_Slow_Taps: Wheter or not to drop extra audio onsets in between two taps (i.e., someone missed a tap)

TapDrift:

BPM: BPM used for inferring audio timing
Raw_Audio: Whether or not to use the "raw audio feed" to determine audio onsets.
If true, will analyze the video's audio to determine onset times
If false, will infer audio onsets based on BPM config value

CirclePositions:

FINGER: Which finger index to derive positions from. 
See mediapipe hand model documentation for what each index is
FPS: FPS of video. MAKE SURE TO MATCH WITH Data

CircleDetector:

Raidus_Variation_Thresh: How much, as a measure of variance, a radius can vary across a Circle
Curvature_Smoothness_Thresh: How much a circle can be "not curvy" before missing Detection
Min_Rotation_Radians: How much rotation must occur before a circle is counted. 
Current value is 2pi
Min_Circle_Duration: Shortest a circular motion can last, in seconds
Moving_Average_Window: Window for taking a moving average of trajectory. Similar to "Smoothing_Window" for taps
Require_Quadrants: Enables/Disables quadrant checking (needs "4 extremes" from center)
Plot Circles: Enables/Disables plotting of detected circles
