// FOLLOWING STANDARD CODE, ANYTHING THAT IS ALL CAPS IS A CONFIG VALUE

// CONFIG STARTS HERE

// Hardcoded flow for tasks. See dictionaries for how flow progresses
// If hardcoded flow is left undefined or empty, flow is generated randomly
// Indexing:
/*

0: Tap Task, No Audio
1: Tap Task, With Audio
2: Circle Task, No Audio
3: Circle Task, With Audio

*/
const HARDCODED_FLOW = [1, 0, 3, 2]

// Number of tap practice trials, actual tap trials per block, and total blocks
// Total trials = TAP_NUMTRIALS * TAP_NUMBLOCKS
// (for with-audio tasks, this is per audio condition, see HARDCODED_AUDIO_FLOW)
const TAP_NOAUDIO_NUMPRACTICE = 0;
const TAP_NOAUDIO_NUMTRIALS = 1;
const TAP_NOAUDIO_NUMBLOCKS = 1;

const TAP_AUDIO_NUMPRACTICE = TAP_NOAUDIO_NUMPRACTICE
const TAP_AUDIO_NUMTRIALS = TAP_NOAUDIO_NUMTRIALS
const TAP_AUDIO_NUMBLOCKS = TAP_NOAUDIO_NUMBLOCKS

// Same as TAP variables above
const CIRCLE_NOAUDIO_NUMPRACTICE = TAP_NOAUDIO_NUMPRACTICE
const CIRCLE_NOAUDIO_NUMTRIALS = TAP_NOAUDIO_NUMTRIALS
const CIRCLE_NOAUDIO_NUMBLOCKS = TAP_NOAUDIO_NUMBLOCKS

const CIRCLE_AUDIO_NUMPRACTICE = TAP_NOAUDIO_NUMPRACTICE
const CIRCLE_AUDIO_NUMTRIALS = TAP_NOAUDIO_NUMTRIALS
const CIRCLE_AUDIO_NUMBLOCKS = TAP_NOAUDIO_NUMBLOCKS

// How long the video will record for, in seconds, for NO-AUDIO trials.
// With-audio trials record for the lengthSec of their audio condition (see AUDIO_SOURCES)
// (also not in doCountDown, countdown values currently go unused)
const TRIAL_TIME_SEC  = 10;

// Audio for "audio included" trials. Each entry is one audio condition,
// referred to by its index (0, 1, 2, ...) in HARDCODED_AUDIO_FLOW and in recorded filenames
// src: path to the audio file
// lengthSec: how long trials with this audio record for, in seconds
// MAKE SURE EACH lengthSec MATCHES ITS CLIP'S DURATION (a console warning fires if they differ)
const AUDIO_SOURCES = [
    { src: "./assets/BBNTempo_700_loc0_step0_perc0_sync.wav", lengthSec: 22 },
    { src: "./assets/ComboTempo_700_loc0_step0_perc0_sync.wav", lengthSec: 21 },
    { src: "./assets/GlissTempo_700_loc0_step0_perc0_sync.wav", lengthSec: 22 }
];

// Hardcoded order of audio conditions for each with-audio task, keyed by task index (see flow indexing above)
// Each audio condition in a task's order gets its own full set of recorded blocks, in that order.
// Practice trials (if any) play the first audio condition in the task's order.
// If a task's entry is left undefined or empty, its audio order is generated randomly
// Example with two conditions:
//   AUDIO_SOURCES = [
//       { src: "./assets/click-track-60bpm.wav", lengthSec: 10 },
//       { src: "./assets/click-track-90bpm.wav", lengthSec: 15 }
//   ]
//   HARDCODED_AUDIO_FLOW = { 1: [0, 1], 3: [1, 0] }
const HARDCODED_AUDIO_FLOW = {

}


// Text values for non-tap/circle screens

// Header text that shows on the first slide to enter participant ID
const WELCOME_HEADER = "Welcome! Please enter your participant ID, and press \"Next\"!";

// Header text for non-specific instructions
const BASIC_INSTRUCTIONS_HEADER = "Read the task instructions below, and press \"Next\" when you have finished";

// Variable Length Pretest Instructions
// Slide format is: BASIC_INSTRUCTIONS_HEADER\nPRETEST_INSTRUCTIONS[state-1]
// state-1 because 0 state is participant ID entry
const PRETEST_INSTRUCTIONS = [
    "In this experiment you will do several different types of repetitive hand movements while video is being recorded of your hand.",

    "Some conditions will have sound, others will not.",

    "You will complete 4 trials of each task. Before starting the experimental trials, you will have a chance to practice twice.",

    "You will be able to take a break from the task whenever necessary.",

    "Press next to get detailed instructions for your first task."
];


// Text values for tap/circle screens

// Header for tap task instructions/overview
const TAP_INSTR_HEADER = "Tapping Task: Overview";

// Header for tap task practice trials
const TAP_PRACTICE_HEADER = "Tapping Task: Practice";

// Header for tap task recorded trials
const TAP_TRIAL_HEADER = "Tapping Task: Trials";

// Header for circle task instructions/overview
const CIRCLE_INSTR_HEADER = "Circle Task: Overview";

// Header for circle task practice trials
const CIRCLE_PRACTICE_HEADER = "Circle Task: Practice";

// Header for circle task recorded trials
const CIRCLE_TRIAL_HEADER = "Circle Task: Trials";

// Initial instructions shown for practice trials (circle or tap)
const PRACTICE_INSTR_TEXT = "The first practice trials are for familiarization with the task. Afterwards, recorded trials will begin.";

// Text shown before a practice trial starts (circle or tap)
const PRACTICE_PREPARE_TEXT = "Press Next to begin your practice trial.";

// Text shown for completing a practice trial (circle or tap)
const PRACTICE_COMPLETE_TEXT = "You completed a practice trial! Press Next when you are ready to begin your next practice trial";

// Text shown for completion of all practice trials (circle or tap)
const ALL_PRACTICE_COMPLETE_TEXT = "You have completed all practice trials! Press Next to begin recorded trials";

// Text shown before a trial starts (circle or tap)
const TRIAL_PREPARE_TEXT = "Press Next to begin the recorded trial";

// Text shown for completing a trial (circle or tap)
const TRIAL_COMPLETE_TEXT = "You completed a trial! Press Next when you are ready to begin your next trial";

// Text shown for completing a non-practice (recorded) block (circle or tap)
const BLOCK_COMPLETE_TEXT = "You completed a block! Press Next to move on to the next block!";

// Header for experiment complete (all tasks finished)
const EXPR_COMPLETE_HEADER = "Experiment Complete"

// Text for experiment complete (all tasks finished)
const EXPR_COMPLETE_TEXT = "All tasks complete. Thank you!"

// Dictionary for task overviews. Indexing:
/*

0: Tap Task, No Audio
1: Tap Task, With Audio
2: Circle Task, No Audio
3: Circle Task, With Audio

*/
const TASK_OVERVIEWS = {
    0: [
        "In this task, you will tap to the beat of an audio recording.",
        "Try to match when you tap with when the click happens in the recording."
    ],
    1: [
        "In this task, you will tap at a consistent speed.",
        "Maintain a steady rhythm for 10 seconds."
    ],
    2: [
        "In this task, you will move your hand in a circular motion to a beat.",
        "Try to match when each circle completes with the click."
    ],
    3: [
        "In this task, you will move your hand in a smooth circular motion.",
        "Keep the motion continuous for 10 seconds."
    ]
}


// CONFIG ENDS HERE

// LOCAL VARIABLES (DO NOT MODIFY)

flow = []
expIndex = 0
device = null;
trial = 1;
block = 0;

// Order of audio conditions for the current task (empty for no-audio tasks),
// and the position of the current audio condition within that order
audioFlow = []
audioIndex = 0

const taskDictionary = {
    0: tap_task,
    1: tap_task,
    2: circle_task,
    3: circle_task
}

const withAudioDictionary = {
    0: false,
    1: true,
    2: false,
    3: true
}

// We start with pre-task instructions
let stateFunction = pretest_control_flow;

// Page initialization and grabbing video device
window.addEventListener('load', async () => {
  let stateVal = Number(document.getElementById("state-value").value);
  let currTask = Number(document.getElementById("currTask").value);
  const audio = document.getElementById("clicktrack");
  audio.src = AUDIO_SOURCES[0].src;
  audio.load();
  device = await navigator.mediaDevices.getUserMedia({video: 
    {frameRate: {ideal: 60, max: 120}}, audio: true});
  if (currTask != -1){
    stateFunction = taskDictionary[currTask]
  }
  stateFunction(stateVal);
});

// Goes to next state (current logic handler function controls what page loads on given state)
function next_state(){
    let stateVal = Number(document.getElementById("state-value").value)
    console.log(stateVal);
    stateVal += 1
    document.getElementById("state-value").value = String(stateVal)
    stateFunction(stateVal)
}

// Goes to previous state (current logic handler function controls what page loads on given state)
function prev_state(){
    let stateVal = Number(document.getElementById("state-value").value)
    console.log(stateVal)
    stateVal -= 1
    if (stateVal < 0){
        stateVal = 0;
    }
    document.getElementById("state-value").value = String(stateVal)
    stateFunction(stateVal)
}

// Easy sleep function
const sleep = m => new Promise(r => setTimeout(r, m))

// Logic handler for pre-task instructions
function pretest_control_flow(state){

    const FINAL_PRETEST_STATE = PRETEST_INSTRUCTIONS.length + 1;

    if (state > 0 && state != 1){
        enableDisablePrev(true);
        document.getElementById("id-input-form").style.display="none"
    } else {
        enableDisablePrev(false);
        document.getElementById("id-input-form").style.display="flex"
    }

    if (state != 2){
        document.getElementById("loader-gif").style.display = "none"
    }

    switch (state){
        case 0:
            pretest_state_0();
            break;

        case 1:
            document.getElementById("button-next").style.opacity = 1
            document.getElementById("button-next").style.pointerEvents = "all"

            if (checkSubmit()){
                document.getElementById("participant-id-error").style.display = "none"
                enableDisablePrev(true)
                document.getElementById("id-input-form").style.display="none"
            } else {
                document.getElementById("participant-id-error").style.display = "block"
                enableDisablePrev(false)
                document.getElementById("state-value").value = String(0)
                return
            }

            pretest_instruction_state(0);
            break;

        default:

            if (state >= 2 && state <= PRETEST_INSTRUCTIONS.length){

                pretest_instruction_state(state - 1);
                return;
            }

            if (state == FINAL_PRETEST_STATE){
                task_flow_init();
            }

            break;
    }
}

// Verifies integrity of participant id input
function checkSubmit(){
    const partInput = document.getElementById("participant-id")
    let partInputVal = partInput.value
    if (!isNaN(Number(partInputVal)) && partInputVal.length != 0){
        document.getElementById("hidden-participant-id").value = Number(partInputVal)
        return true
    }
    return false
}

function pretest_state_0(){
    document.getElementById("header-text").innerText = WELCOME_HEADER;
    document.getElementById("instructions-text").innerText = ""
}

function pretest_instruction_state(index){
    document.getElementById("header-text").innerText =
        BASIC_INSTRUCTIONS_HEADER;

    document.getElementById("instructions-text").innerText =
        PRETEST_INSTRUCTIONS[index];
}

// Spins up task flow after pre-task instructions are completed
function task_flow_init(){
    console.log("init called!")
    document.getElementById("state-value").value = 0;
    console.log("init called!")
    // Only build the flow once. This runs again after every task, and
    // regenerating here would reshuffle a random flow mid-experiment
    if (flow.length == 0){
        if (HARDCODED_FLOW.length != 0){
            flow = HARDCODED_FLOW
        } else {
            flow = generateRandomFlow();
        }
    }
    if (expIndex >= flow.length){
        enableDisableNext(false)
        enableDisablePrev(false)
    
        document.getElementById("header-text").innerText = EXPR_COMPLETE_HEADER;
    
        document.getElementById("instructions-text").innerText = EXPR_COMPLETE_TEXT;
    
        return;
    }

    // Build the audio condition order for this task (stays empty for no-audio tasks)
    audioFlow = []
    audioIndex = 0
    if (withAudioDictionary[flow[expIndex]]){
        const hardcodedAudioFlow = HARDCODED_AUDIO_FLOW[flow[expIndex]];
        if (hardcodedAudioFlow && hardcodedAudioFlow.length != 0){
            audioFlow = hardcodedAudioFlow
        } else {
            audioFlow = generateRandomFlow(AUDIO_SOURCES.map((_, i) => i));
        }
        loadAudioCondition(audioFlow[0]);
    }

    document.getElementById("currTask").value = flow[expIndex]

    stateFunction = taskDictionary[flow[expIndex]]
    
    stateFunction(0)
}

// Handles transitions between variable instruction lengths for a given task
function task_intro_state(taskType, index){
    document.getElementById("header-text").innerText =
        (taskType < 2) ? TAP_INSTR_HEADER : CIRCLE_INSTR_HEADER;

    document.getElementById("instructions-text").innerText =
        TASK_OVERVIEWS[taskType][index];
}

// Logic handler for the tap task (audio and no audio)
function tap_task(state){
    console.log("state called!")
    if (block > (withAudioDictionary[flow[expIndex]] ? TAP_AUDIO_NUMBLOCKS : TAP_NOAUDIO_NUMBLOCKS)){
        // Audio conditions left for this task: rerun the recorded blocks with the next one.
        // We arrive here from tap_state_8 at state 5, so this falls through to the block-complete screen
        if (audioIndex < audioFlow.length - 1){
            audioIndex += 1
            loadAudioCondition(audioFlow[audioIndex])
            block = 1;
            trial = 1;
        } else {
            expIndex += 1
            block = 0;
            trial = 1;
            task_flow_init();
            return;
        }
    }
    if (block == 0){
        const introLength = TASK_OVERVIEWS[flow[expIndex]].length;

        if (state < introLength){
            task_intro_state(flow[expIndex], state);
            return;
        }

        // Zero practice trials configured: skip straight to the first recorded block
        if ((withAudioDictionary[flow[expIndex]] ? TAP_AUDIO_NUMPRACTICE : TAP_NOAUDIO_NUMPRACTICE) <= 0){
            block = 1;
            enableDisablePrev(false);
            document.getElementById("countdown-num").style.display = "none";
            document.getElementById("state-value").value = 1;
            tap_task(1);
            return;
        }
    
        let shiftedState = state - introLength;
    
        switch (shiftedState){
            case 0:
                tap_state_1()
                break;
            case 1:
                tap_state_2()
                break;
            case 2:
                tap_state_3(withAudioDictionary[flow[expIndex]])
                break;
            case 3:
                tap_state_4();
                break;
            case 4:
                document.getElementById("state-value").value = introLength + 1
                tap_task(introLength + 1)
                break;
        }
    } else {
        switch (state){
            case 0:
                tap_state_5()
                break;
            case 1:
                tap_state_6()
                break;
            case 2:
                tap_state_7(withAudioDictionary[flow[expIndex]])
                break;
            case 3:
                tap_state_8()
                break;
            case 4:
                document.getElementById("state-value").value = 1
                tap_task(1)
                break;
            case 5:
                tap_state_9()
                break;
            case 6:
                document.getElementById("state-value").value = 1
                tap_task(1)
                break;
        }
    }
}

// Logic handler for the circle task (audio and no audio)
function circle_task(state){
    console.log("circle state called!")

    if (block > (withAudioDictionary[flow[expIndex]] ? CIRCLE_AUDIO_NUMBLOCKS : CIRCLE_NOAUDIO_NUMBLOCKS)){
        // Audio conditions left for this task: rerun the recorded blocks with the next one.
        // We arrive here from circle_state_8 at state 5, so this falls through to the block-complete screen
        if (audioIndex < audioFlow.length - 1){
            audioIndex += 1
            loadAudioCondition(audioFlow[audioIndex])
            block = 1;
            trial = 1;
        } else {
            expIndex += 1
            block = 0;
            trial = 1;
            task_flow_init();
            return;
        }
    }

    // PRACTICE BLOCK
    if (block == 0){
        const introLength = TASK_OVERVIEWS[flow[expIndex]].length;

        if (state < introLength){
            task_intro_state(flow[expIndex], state);
            return;
        }

        // Zero practice trials configured: skip straight to the first recorded block
        if ((withAudioDictionary[flow[expIndex]] ? CIRCLE_AUDIO_NUMPRACTICE : CIRCLE_NOAUDIO_NUMPRACTICE) <= 0){
            block = 1;
            enableDisablePrev(false);
            document.getElementById("countdown-num").style.display = "none";
            document.getElementById("state-value").value = 1;
            circle_task(1);
            return;
        }
    
        let shiftedState = state - introLength;
    
        switch (shiftedState){
            case 0:
                circle_state_1()
                break;
    
            case 1:
                circle_state_2()
                break;
    
            case 2:
                circle_state_3(withAudioDictionary[flow[expIndex]])
                break;
    
            case 3:
                circle_state_4()
                break;
    
            case 4:
                document.getElementById("state-value").value = introLength + 1
                circle_task(introLength + 1)
                break;
        }
    }

    // REAL TRIAL BLOCK
    else {
        switch (state){
            case 0:
                circle_state_5()
                break;

            case 1:
                circle_state_6()
                break;

            case 2:
                circle_state_7(withAudioDictionary[flow[expIndex]])
                break;

            case 3:
                circle_state_8()
                break;

            case 4:
                document.getElementById("state-value").value = 1
                circle_task(1)
                break;

            case 5:
                circle_state_9()
                break;

            case 6:
                document.getElementById("state-value").value = 1
                circle_task(1)
                break;
        }
    }
}

function tap_state_1(){
    document.getElementById("countdown-num").style.display = "none";
    document.getElementById("header-text").innerText = TAP_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = PRACTICE_INSTR_TEXT;
}

function tap_state_2(){
    document.getElementById("countdown-num").style.display = "none";
    document.getElementById("header-text").innerText = TAP_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = PRACTICE_PREPARE_TEXT;
}

// This is where practice trials are ran for taps.
function tap_state_3(isAudio){
    document.getElementById("header-text").innerText = TAP_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = ""
    enableDisableNext(false)
    enableDisablePrev(false)
    doCountdownRecord(3, getTrialLengthSec(isAudio), isAudio, true)
}

function tap_state_4(){
    enableDisableNext(true)
    enableDisablePrev(false)
    trial += 1
    if (trial > (withAudioDictionary[flow[expIndex]] ? TAP_AUDIO_NUMPRACTICE : TAP_NOAUDIO_NUMPRACTICE)){
        block += 1
        document.getElementById("state-value").value = 0
        trial = 1;
        tap_task(0)
        return;
    }
    document.getElementById("header-text").innerText = TAP_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = PRACTICE_COMPLETE_TEXT;
}

function tap_state_5(){
    document.getElementById("header-text").innerText = TAP_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = ALL_PRACTICE_COMPLETE_TEXT;
}

function tap_state_6(){
    document.getElementById("header-text").innerText = TAP_TRIAL_HEADER;
    document.getElementById("instructions-text").innerText = TRIAL_PREPARE_TEXT;
}

// This is where the actual trial data is recorded for taps!
function tap_state_7(isAudio){
    document.getElementById("header-text").innerText = TAP_TRIAL_HEADER
    document.getElementById("instructions-text").innerText = ""
    enableDisableNext(false)
    enableDisablePrev(false)
    doCountdownRecord(3, getTrialLengthSec(isAudio), isAudio, false)
}

function tap_state_8(){
    enableDisableNext(true)
    enableDisablePrev(false)
    trial += 1
    if (trial > (withAudioDictionary[flow[expIndex]] ? TAP_AUDIO_NUMTRIALS : TAP_NOAUDIO_NUMTRIALS)){
        block += 1
        document.getElementById("state-value").value = 5;
        trial = 1;
        tap_task(5)
        return;
    }
    document.getElementById("header-text").innerText = TAP_TRIAL_HEADER
    document.getElementById("instructions-text").innerText = TRIAL_COMPLETE_TEXT
}

function tap_state_9(){
    document.getElementById("header-text").innerText = TAP_TRIAL_HEADER
    document.getElementById("instructions-text").innerText = BLOCK_COMPLETE_TEXT;
}

function circle_state_1(){
    document.getElementById("countdown-num").style.display = "none";

    document.getElementById("header-text").innerText = CIRCLE_PRACTICE_HEADER;
    document.getElementById("instructions-text").innerText = PRACTICE_INSTR_TEXT;
}

function circle_state_2(){
    document.getElementById("countdown-num").style.display = "none";

    document.getElementById("header-text").innerText = CIRCLE_PRACTICE_HEADER
    document.getElementById("instructions-text").innerText =
    PRACTICE_PREPARE_TEXT;
}

// This is where practice trials are ran for circles.
function circle_state_3(isAudio){
    document.getElementById("header-text").innerText = CIRCLE_PRACTICE_HEADER
    document.getElementById("instructions-text").innerText = ""

    enableDisableNext(false)
    enableDisablePrev(false)

    doCountdownRecord(3, getTrialLengthSec(isAudio), isAudio, true)
}

function circle_state_4(){
    enableDisableNext(true)
    enableDisablePrev(false)

    trial += 1

    if (trial > (withAudioDictionary[flow[expIndex]] ? CIRCLE_AUDIO_NUMPRACTICE : CIRCLE_NOAUDIO_NUMPRACTICE)){
        block += 1
        document.getElementById("state-value").value = 0
        trial = 1;

        circle_task(0)
        return;
    }

    document.getElementById("header-text").innerText = CIRCLE_PRACTICE_HEADER
    document.getElementById("instructions-text").innerText = PRACTICE_COMPLETE_TEXT;
        
}

function circle_state_5(){
    document.getElementById("header-text").innerText = CIRCLE_PRACTICE_HEADER
    document.getElementById("instructions-text").innerText = ALL_PRACTICE_COMPLETE_TEXT;
}

function circle_state_6(){
    document.getElementById("header-text").innerText = CIRCLE_TRIAL_HEADER;
    document.getElementById("instructions-text").innerText = TRIAL_PREPARE_TEXT;
}

// This is where the actual trial data is recorded for circles!
function circle_state_7(isAudio){
    document.getElementById("header-text").innerText = CIRCLE_TRIAL_HEADER
    document.getElementById("instructions-text").innerText = ""

    enableDisableNext(false)
    enableDisablePrev(false)

    doCountdownRecord(3, getTrialLengthSec(isAudio), isAudio, false)
}

function circle_state_8(){
    enableDisableNext(true)
    enableDisablePrev(false)

    trial += 1

    if (trial > (withAudioDictionary[flow[expIndex]] ? CIRCLE_AUDIO_NUMTRIALS : CIRCLE_NOAUDIO_NUMTRIALS)){
        block += 1

        document.getElementById("state-value").value = 5;
        trial = 1;

        circle_task(5)
        return;
    }

    document.getElementById("header-text").innerText = CIRCLE_TRIAL_HEADER
    document.getElementById("instructions-text").innerText = TRIAL_COMPLETE_TEXT
        
}

function circle_state_9(){
    document.getElementById("header-text").innerText = CIRCLE_TRIAL_HEADER
    document.getElementById("instructions-text").innerText =
        BLOCK_COMPLETE_TEXT;
}


// Enables/disables the "Previous" button
function enableDisablePrev(enable){
    if (enable){
        document.getElementById("button-prev").style.opacity = 1
        document.getElementById("button-prev").style.pointerEvents = "all"
    } else {
        document.getElementById("button-prev").style.opacity = 0.25
        document.getElementById("button-prev").style.pointerEvents = "none"
    }
}

// Enables/disables the "Next" button
function enableDisableNext(enable){
    if (enable){
        document.getElementById("button-next").style.opacity = 1
        document.getElementById("button-next").style.pointerEvents = "all"
    } else {
        document.getElementById("button-next").style.opacity = 0.25
        document.getElementById("button-next").style.pointerEvents = "none"
    }
}

// Starts the "Wait..." period before a trial starts
function doCountdownRecord(countdownMax, videoLength, isAudio, isPractice){
    const countDownText = document.getElementById("countdown-num")
    let currNum = countdownMax-1
    countDownText.style.color = "black";
    countDownText.innerText = "Wait..."
    countDownText.style.display = "block";
    const countdownInterval = setInterval(() => {
        if (currNum == 0){
            clearInterval(countdownInterval)
            beginRecordWrapper(videoLength, isAudio, isPractice);
            return;
        }
        currNum--
    }, 1000)
}

// Starts the recording (and audio) if applicable for a trial. 
// If isPractice is true, no actual data is recorded, but the trial "plays out"
// If isPractice is false, a trial is ran as normal and data is recorded
// Format for filename:
// (participantID)_(circle/tap)_(withAudioN/noAudio)_(block)_(trial)
// where N is the audio condition's index in AUDIO_SOURCES
async function beginRecordWrapper(videoLength, isAudio, isPractice){
    const countUpText = document.getElementById("countup-num")
    const countDownText = document.getElementById("countdown-num")
    let currNum = 1;
    const partID =  document.getElementById("hidden-participant-id").value;
    let taskName = "circle"
    let audioName = "noAudio"
    if (flow[expIndex] < 2){
        taskName = "tap"
    }
    if (isAudio){
        audioName = `withAudio${audioFlow[audioIndex]}`
    }
    if (isAudio){
        playAudio();
    }
    if (!isPractice){
        countDownText.innerText = "RECORDING"
        countDownText.style.color = "red";
        await begin_record(videoLength, `${partID}_${taskName}_${audioName}_${block}_${trial}`, device);
    } else {
        countDownText.innerText = "PRACTICE!"
        countDownText.style.color = "black";
        await sleep(videoLength * 1000)
    }
    endRecordWrapper(isAudio);
    countDownText.style.display = "none"
    countUpText.style.display = "none"
    return;
}

// Ends the recording (and audio) if applicable for a given trial
function endRecordWrapper(isAudio){
    console.log("recording complete, next state!")
    if (isAudio){
        stopAudio();
    }
    next_state();
}

// Starts playing the trial audio
function playAudio(){
    const ct = document.getElementById("clicktrack");
    ct.play();
}

// Stops playing the trial audio
function stopAudio(){
    const ct = document.getElementById("clicktrack");
    ct.pause();
    ct.currentTime = 0;
}

// Swaps the trial audio to the given audio condition (index into AUDIO_SOURCES)
function loadAudioCondition(audioCond){
    const ct = document.getElementById("clicktrack");
    const cond = AUDIO_SOURCES[audioCond];
    // Sanity check that the configured length matches the clip once it loads
    ct.addEventListener("loadedmetadata", () => {
        if (Math.abs(ct.duration - cond.lengthSec) > 0.5){
            console.warn(`Audio condition ${audioCond} (${cond.src}) is ${ct.duration.toFixed(2)}s long, but lengthSec is ${cond.lengthSec}`);
        }
    }, { once: true });
    ct.src = cond.src;
    ct.load();
}

// How long the current trial runs/records for, in seconds
function getTrialLengthSec(isAudio){
    return isAudio ? AUDIO_SOURCES[audioFlow[audioIndex]].lengthSec : TRIAL_TIME_SEC;
}

// Shuffles the given list of condition indices (defaults to the four task conditions)
// Used for both the task flow and each task's audio condition order
function generateRandomFlow(base = [0, 1, 2, 3]) {
    base = base.slice();

    // Fisher-Yates shuffle
    for (let i = base.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [base[i], base[j]] = [base[j], base[i]];
    }

    return base;
}
