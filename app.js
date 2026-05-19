/**
 * J.A.R.V.I.S. Interactive Logic - Enhanced
 */

const stateClasses = ['state-idle', 'state-listening', 'state-processing', 'state-speaking'];
const statusText = document.getElementById('statusText');
const transcriptDisplay = document.getElementById('transcriptText');
const arcReactor = document.getElementById('arcReactor');
const responseOverlay = document.getElementById('jarvisResponse');
const terminalLogs = document.getElementById('terminalLogs');

let targetState = 'idle';
let stateTransitionTimeout = null;

function setState(state) {
    document.body.classList.remove(...stateClasses);
    document.body.classList.add(`state-${state}`);
    targetState = state;

    clearTimeout(stateTransitionTimeout);
    
    switch(state) {
        case 'listening':
            statusText.innerText = 'KALKI LISTENING...';
            statusText.style.color = 'var(--accent-alert)';
            addLog('KALKI ACTIVATED');
            break;
        case 'processing':
            statusText.innerText = 'PROCESSING...';
            statusText.style.color = 'var(--accent-alert)';
            break;
        case 'speaking':
            statusText.innerText = 'KALKI';
            statusText.style.color = '#fff';
            break;
        default:
            statusText.innerText = 'SYSTEM READY';
            statusText.style.color = 'var(--accent-cyan)';
            stateTransitionTimeout = setTimeout(() => {
                statusText.innerText = 'AWAITING ACTIVATION...';
            }, 5000);
    }
}

function addLog(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerText = `> ${message}`;
    terminalLogs.prepend(entry);
    if (terminalLogs.children.length > 20) terminalLogs.removeChild(terminalLogs.lastChild);
}

// Voice Recognition with Kalki Wake Word
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isAwake = false;

if (Recognition) {
    recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        addLog('VOICE SENSORS ONLINE');
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        transcriptDisplay.innerText = transcript.trim();

        const lowerTranscript = transcript.toLowerCase();
        
        // Detect KALKI or JARVIS wake word
        if ((lowerTranscript.includes('kalki') || lowerTranscript.includes('jarvis')) && 
            document.body.classList.contains('state-idle')) {
            isAwake = true;
            addLog('WAKE WORD DETECTED');
            setState('listening');
        }
        
        // Process command when awake and in listening state
        if (isAwake && lowerTranscript && document.body.classList.contains('state-listening')) {
            const command = lowerTranscript.replace(/kalki|jarvis/gi, '').trim();
            if (command) processCommand(command || transcript);
        }
    };

    recognition.onerror = (event) => {
        addLog(`VOICE ERROR: ${event.error}`);
    };

    recognition.onend = () => {
        if (document.body.classList.contains('state-listening') && !isAwake) {
            setState('idle');
        }
        isAwake = false;
    };
}

async function processCommand(text) {
    setState('processing');
    addLog(`CMD: ${text.substring(0, 30)}...`);

    try {
        const response = await fetch('/api/v1/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: text, timestamp: new Date().toISOString() })
        });
        const data = await response.json();
        handleJarvisResponse(data.response);
    } catch (err) {
        addLog('ERROR: CONNECTION FAILED');
        setState('idle');
    }
}

function handleJarvisResponse(text) {
    const formattedText = text.startsWith('Sir') || text.startsWith('sir') ? text : `Sir, ${text}`;
    setState('speaking');
    responseOverlay.innerText = formattedText;
    responseOverlay.style.display = 'block';
    addLog('RESPONSE DELIVERED');

    if (window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(formattedText);
        utterance.rate = 1.0;
        utterance.pitch = 1.1;
        utterance.volume = 1.0;
        utterance.onend = () => {
            setTimeout(() => {
                setState('idle');
                responseOverlay.style.display = 'none';
            }, 3000);
        };
        window.speechSynthesis.speak(utterance);
    } else {
        setTimeout(() => {
            setState('idle');
            responseOverlay.style.display = 'none';
        }, 5000);
    }
}

document.getElementById('btnListen').addEventListener('click', async () => {
    if (recognition) {
        try {
            await initAudio();
            recognition.start();
            setState('listening');
            addLog('MANUAL ACTIVATION');
        } catch(e) {
            addLog('VOICE ENGINE RESTART');
        }
    } else {
        addLog('VOICE API NOT SUPPORTED - SIMULATING');
        setState('listening');
        setTimeout(() => {
            transcriptDisplay.innerText = "Kalki, show system status";
            processCommand("show system status");
        }, 1500);
    }
});

document.getElementById('btnSimulate').addEventListener('click', () => {
    const mockCommands = [
        "Kalki, run system diagnostics",
        "Kalki, check database status",
        "Kalki, what is today's date?",
        "Kalki, who are you?"
    ];
    const cmd = mockCommands[Math.floor(Math.random() * mockCommands.length)];
    transcriptDisplay.innerText = cmd;
    processCommand(cmd);
});

// Audio Visualizer
let audioCtx, analyzer, dataArray, source;

async function initAudio() {
    if (audioCtx) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyzer = audioCtx.createAnalyser();
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyzer);
        analyzer.fftSize = 128;
        dataArray = new Uint8Array(analyzer.frequencyBinCount);
        addLog('AUDIO SENSORS ACTIVE');
    } catch (err) {
        addLog('AUDIO ACCESS DENIED');
    }
}

// Arc Reactor Animation
const canvas = document.getElementById('coreCanvas');
const ctx = canvas?.getContext('2d');
if (canvas && ctx) {
    canvas.width = 160;
    canvas.height = 160;
    
    function drawCore() {
        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let volume = 0;
        
        if (analyzer) {
            analyzer.getByteFrequencyData(dataArray);
            volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        }

        const pulse = 45 + (volume / 255) * 55;
        const opacity = 0.15 + (volume / 255) * 0.6;
        const scale = 1 + (volume / 255) * 0.4;
        arcReactor.style.transform = `scale(${scale})`;

        // Energy core
        const gradient = ctx.createRadialGradient(80, 80, 0, 80, 80, pulse);
        gradient.addColorStop(0, `rgba(0, 240, 255, ${opacity})`);
        gradient.addColorStop(0.5, `rgba(0, 160, 255, ${opacity * 0.5})`);
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(80, 80, pulse, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Inner ring
        ctx.beginPath();
        ctx.arc(80, 80, 35, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 240, 255, 0.9)`;
        ctx.lineWidth = 2;
        ctx.stroke();

        requestAnimationFrame(drawCore);
    }
    drawCore();
}