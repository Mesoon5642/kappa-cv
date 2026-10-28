// Loads entry.js into a fake browser page so the experiment flow can be clicked
// through in Node. Nothing here touches a real camera, audio device or file.

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ENTRY_SRC = fs.readFileSync(path.join(__dirname, "..", "entry.js"), "utf8");

// Swaps the value of config constants in the entry.js source, so tests don't
// depend on whatever the config at the top of entry.js is currently set to.
// Values are plain JS values (serialized with JSON.stringify).
function applyConfig(src, overrides) {
    for (const [name, value] of Object.entries(overrides)) {
        // Matches a one-line `const NAME = ...` or a multi-line `{`/`[` literal closed at column 0
        const re = new RegExp(`^const ${name}\\s*=\\s*(?:[\\[{][ \\t]*\\r?\\n[\\s\\S]*?^[\\]}];?|.*)$`, "m");
        if (!re.test(src)) {
            throw new Error(`Config constant ${name} not found in entry.js`);
        }
        src = src.replace(re, () => `const ${name} = ${JSON.stringify(value)};`);
    }
    return src;
}

function makeElement() {
    return {
        value: "",
        innerText: "",
        style: {},
        src: "",
        currentTime: 0,
        load() {},
        play() {},
        pause() {},
        addEventListener() {},
    };
}

// Creates a fresh experiment page.
// config: config constant overrides (see applyConfig)
// getUserMedia: replacement for the camera request (defaults to resolving immediately)
function loadExperiment(config = {}, { getUserMedia } = {}) {
    const elements = {};
    const el = id => (elements[id] ??= makeElement());

    // Initial values from entry.html
    el("state-value").value = "0";
    el("currTask").value = "-1";
    el("hidden-participant-id").value = "-1";
    el("participant-id").value = "7";

    // What the countdown text said whenever a trial ran
    const recordings = [];
    const practiceRuns = [];
    let loadHandler = null;

    const context = vm.createContext({
        console: { log() {}, warn() {} },
        document: { getElementById: el },
        navigator: { mediaDevices: { getUserMedia: getUserMedia ?? (async () => ({})) } },
        window: { addEventListener: (event, f) => { if (event === "load") loadHandler = f; } },
        // Timers fire on the next turn of the event loop instead of waiting real time.
        // The only timed sleep in entry.js is a practice trial "playing out"
        setTimeout: (f, ms) => {
            if (ms > 0) {
                practiceRuns.push({ lengthSec: ms / 1000, countdown: el("countdown-num").innerText });
            }
            setImmediate(f);
        },
        setInterval: f => {
            const handle = { cleared: false };
            const tick = () => {
                if (handle.cleared) return;
                f();
                setImmediate(tick);
            };
            setImmediate(tick);
            return handle;
        },
        clearInterval: handle => { handle.cleared = true; },
        // Stands in for video_recorder.js
        begin_record: async (lengthSec, filename) => {
            recordings.push({ lengthSec, filename, countdown: el("countdown-num").innerText });
        },
    });

    // The trailing arrow function lets tests read entry.js's top-level consts and variables by name
    const get = vm.runInContext(applyConfig(ENTRY_SRC, config) + "\n;(name => eval(name))", context);

    const screen = () => `${el("header-text").innerText} | ${el("instructions-text").innerText}`;
    const isEnabled = id => el(id).style.pointerEvents !== "none";
    const isComplete = () => el("header-text").innerText === get("EXPR_COMPLETE_HEADER");

    // Waits for any running trial to finish (i.e. until Next can be pressed again)
    async function settle() {
        for (let i = 0; i < 10000; i++) {
            await new Promise(r => setImmediate(r));
            if (isEnabled("button-next") || isComplete()) return;
        }
        throw new Error(`Next never re-enabled on: ${screen()}`);
    }

    const exp = {
        get,
        el,
        screen,
        isEnabled,
        recordings,
        practiceRuns,

        // Runs the page's load handler. Returns its promise (resolves once the camera is granted)
        load() {
            return loadHandler();
        },

        async next() {
            if (!isEnabled("button-next")) {
                throw new Error(`Next is disabled on: ${screen()}`);
            }
            get("next_state")();
            await settle();
        },

        async prev() {
            if (!isEnabled("button-prev")) {
                throw new Error(`Prev is disabled on: ${screen()}`);
            }
            get("prev_state")();
            await settle();
        },

        // Clicks through the welcome and pretest screens, landing on the first task overview
        async skipPretest() {
            const pretestScreens = get("PRETEST_INSTRUCTIONS").length + 1;
            for (let i = 0; i < pretestScreens; i++) {
                await exp.next();
            }
        },

        // Presses Next until Experiment Complete, returning every screen seen (starting with the current one)
        async runToEnd(maxScreens = 500) {
            const screens = [screen()];
            while (!isComplete()) {
                if (screens.length > maxScreens) {
                    throw new Error(`Flow never reached Experiment Complete:\n${screens.join("\n")}`);
                }
                await exp.next();
                screens.push(screen());
            }
            return screens;
        },
    };
    return exp;
}

module.exports = { loadExperiment };
