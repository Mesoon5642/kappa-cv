// Tests for which text shows on which screen in entry.js
// Run from the gui folder with:  node --test
//
// Each test sets its own trial counts / flow / audio config, so changing the config
// at the top of entry.js won't break these. Expected text is looked up by constant
// name, so rewording any of the text values won't break them either.

const test = require("node:test");
const assert = require("node:assert/strict");
const { loadExperiment } = require("./harness");

// Builds config overrides that set the same practice/trial/block counts for every task
function counts({ practice, trials, blocks }) {
    const config = {};
    for (const task of ["TAP", "CIRCLE"]) {
        for (const audio of ["NOAUDIO", "AUDIO"]) {
            config[`${task}_${audio}_NUMPRACTICE`] = practice;
            config[`${task}_${audio}_NUMTRIALS`] = trials;
            config[`${task}_${audio}_NUMBLOCKS`] = blocks;
        }
    }
    return config;
}

const TWO_AUDIO_CONDITIONS = {
    AUDIO_SOURCES: [
        { src: "./assets/test-a.wav", lengthSec: 5 },
        { src: "./assets/test-b.wav", lengthSec: 6 },
    ],
    HARDCODED_AUDIO_FLOW: { 1: [0, 1], 3: [1, 0] },
};

// Expected screen text, in the same "header | text" form as exp.screen().
// Both arguments are constant names (or expressions) from entry.js
const screen = (exp, header, text) => `${exp.get(header)} | ${exp.get(text)}`;

async function startedExperiment(config) {
    const exp = loadExperiment(config);
    await exp.load();
    await exp.skipPretest();
    return exp;
}

const TASKS = [
    { index: 0, name: "tap, no audio", withAudio: false, prefix: "TAP" },
    { index: 1, name: "tap, with audio", withAudio: true, prefix: "TAP" },
    { index: 2, name: "circle, no audio", withAudio: false, prefix: "CIRCLE" },
    { index: 3, name: "circle, with audio", withAudio: true, prefix: "CIRCLE" },
];

test.describe("pretest screens", () => {
    test("welcome screen shows before the camera prompt is answered", () => {
        const exp = loadExperiment({}, { getUserMedia: () => new Promise(() => {}) });
        exp.load();
        assert.equal(exp.el("header-text").innerText, exp.get("WELCOME_HEADER"));
        assert.equal(exp.el("id-input-form").style.display, "flex");
    });

    test("invalid participant ID stays on the welcome screen with an error", async () => {
        const exp = loadExperiment();
        await exp.load();
        exp.el("participant-id").value = "abc";
        await exp.next();
        assert.equal(exp.el("header-text").innerText, exp.get("WELCOME_HEADER"));
        assert.equal(exp.el("participant-id-error").style.display, "block");

        exp.el("participant-id").value = "12";
        await exp.next();
        assert.equal(exp.screen(), screen(exp, "BASIC_INSTRUCTIONS_HEADER", "PRETEST_INSTRUCTIONS[0]"));
        assert.equal(exp.el("participant-id-error").style.display, "none");
        assert.equal(exp.el("id-input-form").style.display, "none");
    });

    test("pretest instructions show in order, then the first task overview", async () => {
        const exp = loadExperiment({ HARDCODED_FLOW: [2] });
        await exp.load();
        const instructions = exp.get("PRETEST_INSTRUCTIONS");
        for (let i = 0; i < instructions.length; i++) {
            await exp.next();
            assert.equal(exp.screen(), screen(exp, "BASIC_INSTRUCTIONS_HEADER", `PRETEST_INSTRUCTIONS[${i}]`));
        }
        await exp.next();
        assert.equal(exp.screen(), screen(exp, "CIRCLE_INSTR_HEADER", "TASK_OVERVIEWS[2][0]"));
    });

    test("Prev walks back through pretest instructions to the welcome screen", async () => {
        const exp = loadExperiment();
        await exp.load();
        await exp.next();
        await exp.next();
        await exp.prev();
        assert.equal(exp.screen(), screen(exp, "BASIC_INSTRUCTIONS_HEADER", "PRETEST_INSTRUCTIONS[0]"));
        await exp.prev();
        assert.equal(exp.el("header-text").innerText, exp.get("WELCOME_HEADER"));
        assert.equal(exp.el("id-input-form").style.display, "flex");
    });
});

test.describe("task overviews", () => {
    for (const task of TASKS) {
        test(`${task.name} (task ${task.index}) shows its own overview lines`, async () => {
            const exp = await startedExperiment({ HARDCODED_FLOW: [task.index], ...counts({ practice: 0, trials: 1, blocks: 1 }) });
            const overview = exp.get(`TASK_OVERVIEWS[${task.index}]`);
            for (let i = 0; i < overview.length; i++) {
                if (i > 0) await exp.next();
                assert.equal(exp.screen(), screen(exp, `${task.prefix}_INSTR_HEADER`, `TASK_OVERVIEWS[${task.index}][${i}]`));
            }
        });

        // Guards against the overview entries being attached to the wrong task number again
        // (no-audio tasks used to tell participants to follow an audio recording)
        test(`${task.name} overview ${task.withAudio ? "mentions" : "doesn't mention"} the audio`, async () => {
            const exp = loadExperiment();
            const text = exp.get(`TASK_OVERVIEWS[${task.index}]`).join(" ");
            const mentionsAudio = /audio|beat|click|recording/i.test(text);
            assert.equal(mentionsAudio, task.withAudio, `Overview for task ${task.index}: "${text}"`);
        });
    }
});

test.describe("trial flow", () => {
    for (const prefix of ["TAP", "CIRCLE"]) {
        const noAudioTask = prefix === "TAP" ? 0 : 2;

        test(`${prefix.toLowerCase()} task with practice, several trials and blocks`, async () => {
            const exp = await startedExperiment({ HARDCODED_FLOW: [noAudioTask], ...counts({ practice: 2, trials: 2, blocks: 2 }) });
            const PRACTICE = `${prefix}_PRACTICE_HEADER`;
            const TRIAL = `${prefix}_TRIAL_HEADER`;
            assert.deepEqual(await exp.runToEnd(), [
                screen(exp, `${prefix}_INSTR_HEADER`, `TASK_OVERVIEWS[${noAudioTask}][0]`),
                screen(exp, `${prefix}_INSTR_HEADER`, `TASK_OVERVIEWS[${noAudioTask}][1]`),
                screen(exp, PRACTICE, "PRACTICE_INSTR_TEXT"),
                screen(exp, PRACTICE, "PRACTICE_PREPARE_TEXT"),
                screen(exp, PRACTICE, "PRACTICE_COMPLETE_TEXT"),
                screen(exp, PRACTICE, "PRACTICE_PREPARE_TEXT"),
                screen(exp, PRACTICE, "ALL_PRACTICE_COMPLETE_TEXT"),
                // Block 1
                screen(exp, TRIAL, "TRIAL_PREPARE_TEXT"),
                screen(exp, TRIAL, "TRIAL_COMPLETE_TEXT"),
                screen(exp, TRIAL, "TRIAL_PREPARE_TEXT"),
                screen(exp, TRIAL, "BLOCK_COMPLETE_TEXT"),
                // Block 2
                screen(exp, TRIAL, "TRIAL_PREPARE_TEXT"),
                screen(exp, TRIAL, "TRIAL_COMPLETE_TEXT"),
                screen(exp, TRIAL, "TRIAL_PREPARE_TEXT"),
                screen(exp, TRIAL, "TASK_COMPLETE_TEXT"),
                screen(exp, "EXPR_COMPLETE_HEADER", "EXPR_COMPLETE_TEXT"),
            ]);
        });

        test(`${prefix.toLowerCase()} task with zero practice goes straight to recorded trials`, async () => {
            const exp = await startedExperiment({ HARDCODED_FLOW: [noAudioTask], ...counts({ practice: 0, trials: 1, blocks: 1 }) });
            assert.deepEqual(await exp.runToEnd(), [
                screen(exp, `${prefix}_INSTR_HEADER`, `TASK_OVERVIEWS[${noAudioTask}][0]`),
                screen(exp, `${prefix}_INSTR_HEADER`, `TASK_OVERVIEWS[${noAudioTask}][1]`),
                screen(exp, `${prefix}_TRIAL_HEADER`, "TRIAL_PREPARE_TEXT"),
                screen(exp, `${prefix}_TRIAL_HEADER`, "TASK_COMPLETE_TEXT"),
                screen(exp, "EXPR_COMPLETE_HEADER", "EXPR_COMPLETE_TEXT"),
            ]);
        });
    }

    test("audio task shows block complete between audio conditions, then task complete", async () => {
        const exp = await startedExperiment({ HARDCODED_FLOW: [1], ...counts({ practice: 0, trials: 1, blocks: 1 }), ...TWO_AUDIO_CONDITIONS });
        assert.deepEqual(await exp.runToEnd(), [
            screen(exp, "TAP_INSTR_HEADER", "TASK_OVERVIEWS[1][0]"),
            screen(exp, "TAP_INSTR_HEADER", "TASK_OVERVIEWS[1][1]"),
            // Audio condition 0
            screen(exp, "TAP_TRIAL_HEADER", "TRIAL_PREPARE_TEXT"),
            screen(exp, "TAP_TRIAL_HEADER", "BLOCK_COMPLETE_TEXT"),
            // Audio condition 1
            screen(exp, "TAP_TRIAL_HEADER", "TRIAL_PREPARE_TEXT"),
            screen(exp, "TAP_TRIAL_HEADER", "TASK_COMPLETE_TEXT"),
            screen(exp, "EXPR_COMPLETE_HEADER", "EXPR_COMPLETE_TEXT"),
        ]);
    });

    test("task complete shows after every task, followed by the next task's overview", async () => {
        const flow = [1, 0, 3, 2];
        const exp = await startedExperiment({ HARDCODED_FLOW: flow, ...counts({ practice: 1, trials: 1, blocks: 2 }), ...TWO_AUDIO_CONDITIONS });
        const screens = await exp.runToEnd();
        const taskComplete = screens
            .map((s, i) => [s, i])
            .filter(([s]) => s.endsWith(` | ${exp.get("TASK_COMPLETE_TEXT")}`))
            .map(([, i]) => i);

        assert.equal(taskComplete.length, flow.length);
        flow.forEach((task, n) => {
            const after = screens[taskComplete[n] + 1];
            const expected = n + 1 < flow.length
                ? screen(exp, flow[n + 1] < 2 ? "TAP_INSTR_HEADER" : "CIRCLE_INSTR_HEADER", `TASK_OVERVIEWS[${flow[n + 1]}][0]`)
                : screen(exp, "EXPR_COMPLETE_HEADER", "EXPR_COMPLETE_TEXT");
            assert.equal(after, expected, `Screen after task ${task} completed`);
        });
    });
});

test.describe("during trials", () => {
    test("recorded trials show RECORDING, practice trials show PRACTICE! and aren't recorded", async () => {
        const exp = await startedExperiment({ HARDCODED_FLOW: [0], ...counts({ practice: 2, trials: 2, blocks: 1 }) });
        await exp.runToEnd();
        assert.deepEqual(exp.practiceRuns.map(r => r.countdown), ["PRACTICE!", "PRACTICE!"]);
        assert.deepEqual(exp.recordings.map(r => r.countdown), ["RECORDING", "RECORDING"]);
    });

    test("countdown is hidden and instructions are blank only while a trial runs", async () => {
        const exp = await startedExperiment({ HARDCODED_FLOW: [0], ...counts({ practice: 0, trials: 2, blocks: 1 }) });
        while (exp.el("instructions-text").innerText !== exp.get("TRIAL_PREPARE_TEXT")) {
            await exp.next();
        }
        exp.get("next_state")(); // start the trial without waiting for it to finish
        assert.equal(exp.el("instructions-text").innerText, "");
        assert.equal(exp.el("countdown-num").style.display, "block");
        assert.equal(exp.el("countdown-num").innerText, "Wait...");
        assert.equal(exp.isEnabled("button-next"), false);

        await assert.rejects(exp.next(), /Next is disabled/);
        while (!exp.isEnabled("button-next")) await new Promise(r => setImmediate(r));
        assert.equal(exp.el("countdown-num").style.display, "none");
        assert.equal(exp.el("instructions-text").innerText, exp.get("TRIAL_COMPLETE_TEXT"));
    });

    test("with-audio recordings are named and timed by their audio condition", async () => {
        const exp = await startedExperiment({ HARDCODED_FLOW: [3, 2], ...counts({ practice: 0, trials: 1, blocks: 1 }), ...TWO_AUDIO_CONDITIONS });
        await exp.runToEnd();
        assert.deepEqual(exp.recordings.map(r => [r.filename, r.lengthSec]), [
            ["7_circle_withAudio1_1_1", 6],
            ["7_circle_withAudio0_1_1", 5],
            ["7_circle_noAudio_1_1", exp.get("TRIAL_TIME_SEC")],
        ]);
    });
});
