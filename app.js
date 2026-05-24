/**
 * KALKI Interactive HUD Logic - Tailwind Edition
 */

const stateClasses = ['state-idle', 'state-listening', 'state-processing', 'state-speaking'];
const statusText = document.getElementById('statusText');
const transcriptDisplay = document.getElementById('transcriptText');
const cmdInput = document.getElementById('cmdInput');
const arcReactor = document.getElementById('arcReactor');
const responseOverlay = document.getElementById('kalkiResponse');
const terminalLogs = document.getElementById('terminalLogs');
const missionList = document.getElementById('missionList');

function setState(state) {
    document.body.classList.remove(...stateClasses);
    document.body.classList.add(`state-${state}`);

    if (statusText) {
        switch(state) {
            case 'listening':
                statusText.innerText = 'LISTENING...';
                statusText.classList.add('text-secondary');
                break;
            case 'processing':
                statusText.innerText = 'PROCESSING...';
                statusText.classList.add('animate-pulse');
                break;
            case 'speaking':
                statusText.innerText = 'KALKI';
                statusText.classList.remove('text-secondary', 'animate-pulse');
                break;
            default:
                statusText.innerText = 'SYSTEM READY';
                statusText.classList.remove('text-secondary', 'animate-pulse');
        }
    }
}

function addLog(message) {
    if (!terminalLogs) return;
    const entry = document.createElement('div');
    entry.className = 'opacity-80';
    entry.innerText = `> ${new Date().toLocaleTimeString()} | ${message}`;
    terminalLogs.prepend(entry);
    if (terminalLogs.children.length > 8) terminalLogs.lastChild.remove();
}

async function refreshMissions() {
    if (!missionList) return;
    try {
        const res = await fetch('/api/v1/tasks');
        const data = await res.json();
        missionList.innerHTML = '';
        if (data.tasks.length === 0) {
            missionList.innerHTML = '<div class="text-on-surface-variant italic">NO ACTIVE MISSIONS</div>';
        } else {
            data.tasks.forEach(task => {
                const item = document.createElement('div');
                item.className = 'p-3 bg-surface-variant/40 border border-primary/5 rounded hover:bg-primary/5 transition-colors cursor-pointer group';
                item.innerHTML = `
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] font-bold text-primary tracking-widest uppercase">${task.priority}</span>
                        <span class="text-[8px] opacity-40">${new Date(task.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="text-xs group-hover:text-primary transition-colors">${task.title}</div>
                `;
                missionList.appendChild(item);
            });
        }
    } catch (err) {
        addLog('ERR: MISSION_SYNC_FAILED');
    }
}

// --- Voice Recognition ---
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (Recognition) {
    recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');

        if (transcriptDisplay) transcriptDisplay.innerText = transcript;

        if (transcript.toLowerCase().includes('kalki') && document.body.classList.contains('state-idle')) {
            addLog('WAKE_WORD_DETECTED');
            setState('listening');
        }
    };

    recognition.onend = () => {
        const finalTranscript = transcriptDisplay ? transcriptDisplay.innerText : '';
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
        handleKalkiResponse(data.response, data.intent);
    } catch (err) {
        addLog('ERR: API_DISCONNECT');
        setState('idle');
    }
}

function handleKalkiResponse(text, intent) {
    setState('speaking');
    if (responseOverlay) {
        responseOverlay.innerText = text;
        responseOverlay.style.display = 'block';
    }
    addLog(`INTENT: ${intent.toUpperCase()}`);

    if (intent.startsWith('task')) {
        refreshMissions();
    }

    if (window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 0.85;
        utterance.onend = () => {
            setTimeout(() => {
                setState('idle');
                if (responseOverlay) responseOverlay.style.display = 'none';
            }, 1500);
        };
        window.speechSynthesis.speak(utterance);
    } else {
        setTimeout(() => {
            setState('idle');
            if (responseOverlay) responseOverlay.style.display = 'none';
        }, 4000);
    }
}

const startListening = async () => {
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
        setState('listening');
        setTimeout(() => {
            if (transcriptDisplay) transcriptDisplay.innerText = "Kalki, list my tasks.";
            setTimeout(() => processCommand("Kalki, list my tasks."), 1000);
        }, 1500);
    }
};

if (document.getElementById('btnListen')) document.getElementById('btnListen').addEventListener('click', startListening);
if (document.getElementById('btnListenMobile')) document.getElementById('btnListenMobile').addEventListener('click', startListening);

if (cmdInput) {
    cmdInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && cmdInput.value.trim()) {
            const cmd = cmdInput.value.trim();
            cmdInput.value = '';
            if (transcriptDisplay) transcriptDisplay.innerText = cmd;
            processCommand(cmd);
        }
    });
}

if (document.getElementById('btnSimulate')) {
    document.getElementById('btnSimulate').addEventListener('click', () => {
        const mockCommands = [
            "Add task manage project archives",
            "List my missions",
            "Scan the directory for files",
            "Kalki, check my email",
            "Run system diagnostics",
            "Find main.py in the archives"
        ];
        const cmd = mockCommands[Math.floor(Math.random() * mockCommands.length)];
        if (transcriptDisplay) transcriptDisplay.innerText = cmd;
        processCommand(cmd);
    });
}

// --- Audio Visualizer ---
let audioCtx, analyzer, dataArray, source;
async function initAudio() {
    if (audioCtx) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyzer = audioCtx.createAnalyser();
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyzer);
        analyzer.fftSize = 64;
        dataArray = new Uint8Array(analyzer.frequencyBinCount);
        addLog('AUDIO_SENSORS_ACTIVE');
    } catch (err) {
        addLog('ERR: MIC_ACCESS_DENIED');
    }
}

// --- Canvas Animation ---
const canvas = document.getElementById('coreCanvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = 120;
    canvas.height = 120;

    function drawCore() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let volume = 0;
        if (analyzer) {
            analyzer.getByteFrequencyData(dataArray);
            volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        }

        const pulse = 40 + (volume / 255) * 40;
        const opacity = 0.15 + (volume / 255) * 0.5;
        const scale = 1 + (volume / 255) * 0.2;
        if (arcReactor) arcReactor.style.transform = `scale(${scale})`;

        ctx.beginPath();
        ctx.arc(60, 60, pulse, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 204, 0, ${opacity})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(60, 60, 30, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255, 204, 0, 0.4)';
        ctx.lineWidth = 1;
        ctx.stroke();

        requestAnimationFrame(drawCore);
    }
    drawCore();
}

refreshMissions();
addLog('KALKI CORE ONLINE');
