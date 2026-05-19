/**
 * J.A.R.V.I.S. Interactive Logic
 */

const stateClasses = ['state-idle', 'state-listening', 'state-processing', 'state-speaking'];
const statusText = document.getElementById('statusText');
const transcriptDisplay = document.getElementById('transcriptText');
const arcReactor = document.getElementById('arcReactor');
const responseOverlay = document.getElementById('jarvisResponse');
const terminalLogs = document.getElementById('terminalLogs');

function setState(state) {
    document.body.classList.remove(...stateClasses);
    document.body.classList.add(`state-${state}`);

    switch(state) {
        case 'listening':
            statusText.innerText = 'LISTENING...';
            break;
        case 'processing':
            statusText.innerText = 'PROCESSING...';
            break;
        case 'speaking':
            statusText.innerText = 'J.A.R.V.I.S.';
            break;
        default:
            statusText.innerText = 'SYSTEM READY';
    }
}

function addLog(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerText = `> ${message}`;
    terminalLogs.prepend(entry);
    if (terminalLogs.children.length > 15) terminalLogs.lastChild.remove();
}

// --- Voice Recognition ---
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (Recognition) {
    recognition = new Recognition();
    // Provide clearer feedback and higher accuracy settings
    recognition.continuous = true;
    recognition.interimResults = false; // only final results for clearer commands
    recognition.lang = 'en-GB'; // British English for consistent pronunciation


    recognition.onstart = () => {
        addLog('VOICE_ENGINE_ONLINE');
    };

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');

        transcriptDisplay.innerText = transcript;

        if (transcript.toLowerCase().includes('jarvis') && document.body.classList.contains('state-idle')) {
            addLog('WAKE_WORD_DETECTED');
            setState('listening');
        }
    };

    recognition.onend = () => {
        const finalTranscript = transcriptDisplay.innerText;
        if (finalTranscript && document.body.classList.contains('state-listening')) {
            processCommand(finalTranscript);
        } else if (document.body.classList.contains('state-listening')) {
            setState('idle');
        }
    };
}

async function processCommand(text) {
    setState('processing');
    addLog(`CMD_IN: ${text.substring(0, 20)}...`);

    try {
        const response = await fetch('/api/v1/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: text,
                timestamp: new Date().toISOString()
            })
        });

        const data = await response.json();
        handleJarvisResponse(data.response);
    } catch (err) {
        addLog('ERR: API_DISCONNECT');
        setState('idle');
    }
}

function handleJarvisResponse(text) {
    // Ensure response addresses the user politely
    const formattedText = text.startsWith('Sir') ? text : `Sir, ${text}`;
    setState('speaking');
    responseOverlay.innerText = formattedText;
    responseOverlay.style.display = 'block';
    addLog('CMD_OUT: SUCCESS');

    // Enhanced speech synthesis for clearer, British‑style voice
    if (window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(formattedText);
        const voices = speechSynthesis.getVoices();
        const britishVoice = voices.find(v => /en-GB/i.test(v.lang));
        if (britishVoice) {
            utterance.voice = britishVoice;
        }
        utterance.rate = 1.0; // natural speed
        utterance.pitch = 1.0; // neutral pitch
        utterance.volume = 1.0;
        utterance.onend = () => {
            setTimeout(() => {
                setState('idle');
                responseOverlay.style.display = 'none';
            }, 2000);
        };
        window.speechSynthesis.speak(utterance);
    } else {
        // fallback display
        setTimeout(() => {
            setState('idle');
            responseOverlay.style.display = 'none';
        }, 5000);
    }
}

// --- Simulations for Testing ---
document.getElementById('btnListen').addEventListener('click', async () => {
    await initAudio();
    if (recognition) {
        try {
            recognition.start();
            setState('listening');
        } catch(e) {
            addLog('INFO: SPEECH_RESTART');
        }
    } else {
        addLog('ERR: SPEECH_API_UNSUPPORTED');
        // Fallback mock
        setState('listening');
        setTimeout(() => {
            transcriptDisplay.innerText = "Jarvis, run system diagnostics.";
            setTimeout(() => processCommand("Jarvis, run system diagnostics."), 1000);
        }, 2000);
    }
});

document.getElementById('btnSimulate').addEventListener('click', () => {
    const mockCommands = [
        "What is the current system uptime?",
        "Check database status, please.",
        "Jarvis, who are you?",
        "Run system diagnostics."
    ];
    const cmd = mockCommands[Math.floor(Math.random() * mockCommands.length)];
    transcriptDisplay.innerText = cmd;
    processCommand(cmd);
});

// --- Audio Visualizer Logic ---
let audioCtx;
let analyzer;
let dataArray;
let source;

async function initAudio() {
    if (audioCtx) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyzer = audioCtx.createAnalyser();
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyzer);
        analyzer.fftSize = 64;
        const bufferLength = analyzer.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        addLog('AUDIO_SENSORS_ACTIVE');
    } catch (err) {
        addLog('ERR: MIC_ACCESS_DENIED');
    }
}

// --- Arc Reactor Canvas Animation ---
const canvas = document.getElementById('coreCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 120;
canvas.height = 120;

function drawCore() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const time = Date.now() * 0.002;
    let volume = 0;

    if (analyzer) {
        analyzer.getByteFrequencyData(dataArray);
        volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
    }

    const pulse = 40 + (volume / 255) * 40;
    const opacity = 0.1 + (volume / 255) * 0.5;

    // Dynamic Scaling based on audio
    const scale = 1 + (volume / 255) * 0.3;
    arcReactor.style.transform = `scale(${scale})`;

    // Core Glow
    ctx.beginPath();
    ctx.arc(60, 60, pulse, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 240, 255, ${opacity})`;
    ctx.fill();

    // Inner Circle
    ctx.beginPath();
    ctx.arc(60, 60, 30, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Pulse circles
    for(let i = 0; i < 3; i++) {
        ctx.beginPath();
        ctx.arc(60, 60, 30 + i * (volume/10), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 240, 255, ${0.3 - i*0.1})`;
        ctx.stroke();
    }

    requestAnimationFrame(drawCore);
}
drawCore();
