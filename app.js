(function() {
  'use strict';

  /* ─── DOM refs ─── */
  const statusText = document.getElementById('statusText');
  const transcriptDisplay = document.getElementById('transcriptText');
  const arcReactor = document.getElementById('arcReactor');
  const responseOverlay = document.getElementById('jarvisResponse');
  const terminalLogs = document.getElementById('terminalLogs');
  const particleCanvas = document.getElementById('particleCanvas');
  const coreCanvas = document.getElementById('coreCanvas');
  const globeCanvas = document.getElementById('globeCanvas');
  const waveformCanvas = document.getElementById('waveformCanvas');
  const streamContent = document.getElementById('streamContent');
  const headerClock = document.getElementById('headerClock');
  const uptimeBadge = document.getElementById('uptimeBadge');
  const threatCount = document.getElementById('threatCount');

  const stateClasses = ['state-idle','state-listening','state-processing','state-speaking'];

  /* ─── Particle System ─── */
  let particles = [];
  const pCtx = particleCanvas.getContext('2d');
  let pW, pH;

  function resizeParticles() {
    pW = particleCanvas.width = window.innerWidth;
    pH = particleCanvas.height = window.innerHeight;
  }
  resizeParticles();
  window.addEventListener('resize', resizeParticles);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * pW;
      this.y = Math.random() * pH;
      this.size = Math.random() * 2.5 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.3 - 0.1;
      this.opacity = Math.random() * 0.5 + 0.1;
      this.hue = Math.random() > 0.6 ? 280 : 180; // purple or cyan
      this.life = Math.random() * 300 + 100;
      this.maxLife = this.life;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      this.life--;
      if (this.life <= 0 || this.x < -10 || this.x > pW + 10 || this.y < -10 || this.y > pH + 10) {
        this.reset();
      }
    }
    draw() {
      const alpha = this.opacity * Math.min(this.life / 50, 1);
      pCtx.beginPath();
      pCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      const color = this.hue === 280
        ? `rgba(144, 0, 255, ${alpha})`
        : `rgba(0, 255, 255, ${alpha})`;
      pCtx.fillStyle = color;
      pCtx.fill();
      if (this.size > 1.5) {
        pCtx.shadowBlur = 6;
        pCtx.shadowColor = this.hue === 280 ? '#90f' : '#0ff';
        pCtx.fill();
        pCtx.shadowBlur = 0;
      }
    }
  }

  function initParticles(count) {
    particles = [];
    for (let i = 0; i < count; i++) particles.push(new Particle());
  }
  initParticles(120);

  function drawParticles() {
    pCtx.clearRect(0, 0, pW, pH);
    for (const p of particles) { p.update(); p.draw(); }
    requestAnimationFrame(drawParticles);
  }
  drawParticles();

  /* ─── 3D Wireframe Globe ─── */
  const gCtx = globeCanvas.getContext('2d');
  let gW, gH;

  function resizeGlobe() {
    const rect = globeCanvas.parentElement.getBoundingClientRect();
    gW = globeCanvas.width = rect.width;
    gH = globeCanvas.height = rect.height;
  }
  resizeGlobe();
  window.addEventListener('resize', resizeGlobe);

  let globeAngle = 0;
  const globePoints = [];
  const globeRadius = 80;

  // Generate icosahedron-like points
  function initGlobe() {
    const phi = Math.PI * (3 - Math.sqrt(5));
    const n = 42;
    for (let i = 0; i < n; i++) {
      const y = 1 - (i / (n - 1)) * 2;
      const r = Math.sqrt(1 - y * y) * globeRadius;
      const theta = phi * i;
      globePoints.push({
        x: Math.cos(theta) * r,
        y: y * globeRadius,
        z: Math.sin(theta) * r
      });
    }
  }
  initGlobe();

  function project3d(x, y, z, rx, ry) {
    // rotate Y
    let x1 = x * Math.cos(ry) + z * Math.sin(ry);
    let y1 = y;
    let z1 = -x * Math.sin(ry) + z * Math.cos(ry);
    // rotate X
    let x2 = x1;
    let y2 = y1 * Math.cos(rx) - z1 * Math.sin(rx);
    let z2 = y1 * Math.sin(rx) + z1 * Math.cos(rx);
    const scale = 400 / (400 + z2);
    return { x: x2 * scale + gW / 2, y: y2 * scale + gH / 2, z: z2, scale };
  }

  function drawGlobe() {
    gCtx.clearRect(0, 0, gW, gH);
    globeAngle += 0.004;

    const rx = Math.sin(globeAngle * 0.3) * 0.2;
    const ry = globeAngle;

    // Project points
    const projected = globePoints.map(p => ({ ...project3d(p.x, p.y, p.z, rx, ry), orig: p }));

    // Draw connections (Delaunay-like: connect nearby points)
    gCtx.strokeStyle = 'rgba(0, 255, 255, 0.08)';
    gCtx.lineWidth = 0.5;
    for (let i = 0; i < projected.length; i++) {
      for (let j = i + 1; j < projected.length; j++) {
        const dx = projected[i].x - projected[j].x;
        const dy = projected[i].y - projected[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 60 && projected[i].z > -globeRadius * 0.5 && projected[j].z > -globeRadius * 0.5) {
          gCtx.beginPath();
          gCtx.moveTo(projected[i].x, projected[i].y);
          gCtx.lineTo(projected[j].x, projected[j].y);
          gCtx.stroke();
        }
      }
    }

    // Draw nodes
    for (const p of projected) {
      const alpha = (p.z + globeRadius) / (globeRadius * 2);
      const size = 1 + alpha * 2;
      gCtx.beginPath();
      gCtx.arc(p.x, p.y, size, 0, Math.PI * 2);
      gCtx.fillStyle = `rgba(0, 255, 255, ${0.2 + alpha * 0.5})`;
      gCtx.fill();
      if (alpha > 0.5) {
        gCtx.shadowBlur = 8;
        gCtx.shadowColor = '#0ff';
        gCtx.fill();
        gCtx.shadowBlur = 0;
      }
    }

    // Outer ring
    gCtx.beginPath();
    gCtx.ellipse(gW / 2, gH / 2, globeRadius * 1.1, globeRadius * 0.3, 0, 0, Math.PI * 2);
    gCtx.strokeStyle = 'rgba(0, 255, 255, 0.06)';
    gCtx.lineWidth = 1;
    gCtx.stroke();

    requestAnimationFrame(drawGlobe);
  }
  drawGlobe();

  /* ─── Enhanced Arc Reactor Core ─── */
  const cCtx = coreCanvas.getContext('2d');
  let cTime = 0;

  function drawCore() {
    if (!cCtx) return;
    const w = 130, h = 130;
    cCtx.clearRect(0, 0, w, h);
    cTime += 0.02;

    let volume = 0;
    if (window.__analyzer) {
      const arr = new Uint8Array(window.__analyzer.frequencyBinCount);
      window.__analyzer.getByteFrequencyData(arr);
      volume = arr.reduce((a, b) => a + b, 0) / arr.length / 255;
    }

    const cx = w / 2, cy = h / 2;
    const pulse = 40 + volume * 30;
    const opacity = 0.2 + volume * 0.5;

    // Plasma energy
    for (let i = 3; i >= 0; i--) {
      const r = pulse + i * 8 + Math.sin(cTime * 2 + i) * 4;
      const grad = cCtx.createRadialGradient(cx, cy, 0, cx, cy, r);
      const a = opacity / (i + 1);
      grad.addColorStop(0, `rgba(0, 240, 255, ${a})`);
      grad.addColorStop(0.3, `rgba(0, 160, 255, ${a * 0.5})`);
      grad.addColorStop(0.6, `rgba(144, 0, 255, ${a * 0.2})`);
      grad.addColorStop(1, 'transparent');
      cCtx.beginPath();
      cCtx.arc(cx, cy, r, 0, Math.PI * 2);
      cCtx.fillStyle = grad;
      cCtx.fill();
    }

    // Inner bright core
    const coreGrad = cCtx.createRadialGradient(cx - 3, cy - 3, 0, cx, cy, 20);
    coreGrad.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    coreGrad.addColorStop(0.3, `rgba(0, 240, 255, ${0.4 + volume * 0.3})`);
    coreGrad.addColorStop(1, 'transparent');
    cCtx.beginPath();
    cCtx.arc(cx, cy, 20 + volume * 8, 0, Math.PI * 2);
    cCtx.fillStyle = coreGrad;
    cCtx.fill();

    // Energy lines
    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2 + cTime * 0.5;
      const len = 25 + Math.sin(cTime * 3 + i) * 10;
      cCtx.beginPath();
      cCtx.moveTo(cx + Math.cos(angle) * 8, cy + Math.sin(angle) * 8);
      cCtx.lineTo(cx + Math.cos(angle) * len, cy + Math.sin(angle) * len);
      cCtx.strokeStyle = `rgba(0, 255, 255, ${0.1 + volume * 0.3})`;
      cCtx.lineWidth = 1.5;
      cCtx.stroke();
    }

    // Orbital particles around rings
    for (let r = 0; r < 3; r++) {
      const count = r === 0 ? 4 : (r === 1 ? 6 : 8);
      const radius = 45 + r * 20;
      for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2 + cTime * (0.5 + r * 0.2);
        const px = cx + Math.cos(angle) * radius;
        const py = cy + Math.sin(angle) * radius;
        const size = 1.5 + Math.sin(cTime * 2 + i + r) * 0.5;
        cCtx.beginPath();
        cCtx.arc(px, py, size, 0, Math.PI * 2);
        cCtx.fillStyle = r === 0 ? 'rgba(0, 255, 255, 0.8)' :
                         r === 1 ? 'rgba(144, 0, 255, 0.6)' :
                                   'rgba(0, 160, 255, 0.5)';
        cCtx.fill();
        cCtx.shadowBlur = 6;
        cCtx.shadowColor = r === 0 ? '#0ff' : '#90f';
        cCtx.fill();
        cCtx.shadowBlur = 0;
      }
    }

    requestAnimationFrame(drawCore);
  }
  drawCore();

  /* ─── Waveform Visualizer ─── */
  const wCtx = waveformCanvas.getContext('2d');
  let wW, wH;

  function resizeWaveform() {
    const rect = waveformCanvas.parentElement.getBoundingClientRect();
    wW = waveformCanvas.width = rect.width;
    wH = waveformCanvas.height = rect.height;
  }
  resizeWaveform();
  window.addEventListener('resize', resizeWaveform);

  function drawWaveform() {
    wCtx.clearRect(0, 0, wW, wH);
    let vol = 0;
    if (window.__analyzer) {
      const arr = new Uint8Array(window.__analyzer.frequencyBinCount);
      window.__analyzer.getByteFrequencyData(arr);
      const bars = 48;
      const barW = wW / bars;
      for (let i = 0; i < bars; i++) {
        const idx = Math.floor(i / bars * arr.length);
        const val = arr[idx] / 255;
        const h = val * wH * 0.8;
        const alpha = 0.2 + val * 0.6;
        wCtx.fillStyle = `rgba(0, 255, 255, ${alpha})`;
        wCtx.fillRect(i * barW + 1, wH - h, barW - 2, h);
      }
      vol = arr.reduce((a, b) => a + b, 0) / arr.length / 255;
    }
    if (vol > 0.01) {
      arcReactor.style.transform = `scale(${1 + vol * 0.15})`;
    }
    requestAnimationFrame(drawWaveform);
  }
  drawWaveform();

  /* ─── Data Stream Waterfall ─── */
  const hexChars = '0123456789ABCDEF';
  function updateDataStream() {
    let line = '';
    for (let i = 0; i < 40 + Math.random() * 20; i++) {
      line += hexChars[Math.floor(Math.random() * 16)];
      if (i % 4 === 3) line += ' ';
    }
    streamContent.innerHTML = streamContent.innerHTML + '\n' + line;
    const lines = streamContent.innerHTML.split('\n');
    if (lines.length > 20) {
      streamContent.innerHTML = lines.slice(-20).join('\n');
    }
    setTimeout(updateDataStream, 80 + Math.random() * 120);
  }
  updateDataStream();

  /* ─── Clock ─── */
  function updateClock() {
    const now = new Date();
    headerClock.textContent = now.toTimeString().split(' ')[0];
  }
  setInterval(updateClock, 1000);
  updateClock();

  /* ─── System Metrics Polling ─── */
  function updateGauge(id, value, color) {
    const arc = document.getElementById(id);
    if (!arc) return;
    const circumference = 314.16;
    const offset = circumference - (value / 100) * circumference;
    arc.style.strokeDashoffset = offset;
    arc.style.stroke = color || '#0ff';
  }

  async function pollMetrics() {
    try {
      const res = await fetch('/api/v1/metrics');
      const data = await res.json();
      if (data.status === 'success') {
        updateGauge('cpuArc', data.cpu, data.cpu > 80 ? '#f30' : data.cpu > 50 ? '#ff0' : '#0ff');
        updateGauge('memArc', data.memory, data.memory > 80 ? '#f30' : data.memory > 50 ? '#ff0' : '#0ff');
        updateGauge('diskArc', data.disk, data.disk > 80 ? '#f30' : data.disk > 50 ? '#ff0' : '#0ff');
        document.getElementById('cpuVal').textContent = Math.round(data.cpu);
        document.getElementById('memVal').textContent = Math.round(data.memory);
        document.getElementById('diskVal').textContent = Math.round(data.disk);
        uptimeBadge.textContent = data.uptime;
      }
    } catch (_) {}
    setTimeout(pollMetrics, 2000);
  }
  pollMetrics();

  /* ─── State Management ─── */
  let targetState = 'idle';
  let stateTransitionTimeout = null;

  function setState(state) {
    document.body.classList.remove(...stateClasses);
    document.body.classList.add(`state-${state}`);
    targetState = state;
    clearTimeout(stateTransitionTimeout);

    switch (state) {
      case 'listening':
        statusText.innerText = 'LISTENING...';
        break;
      case 'processing':
        statusText.innerText = 'PROCESSING...';
        break;
      case 'speaking':
        statusText.innerText = 'K.A.L.K.I';
        break;
      default:
        statusText.innerText = 'SYSTEM READY';
        stateTransitionTimeout = setTimeout(() => {
          statusText.innerText = 'AWAITING ACTIVATION';
        }, 6000);
    }
  }

  function addLog(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerText = `> ${message}`;
    terminalLogs.prepend(entry);
    if (terminalLogs.children.length > 25) terminalLogs.removeChild(terminalLogs.lastChild);
  }

  /* ─── Voice Recognition ─── */
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition;
  let isAwake = false;

  if (Recognition) {
    recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => addLog('VOICE SENSORS ONLINE');

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      transcriptDisplay.innerText = transcript.trim();

      const lower = transcript.toLowerCase();

      if ((lower.includes('kalki') || lower.includes('jarvis')) &&
          document.body.classList.contains('state-idle')) {
        isAwake = true;
        addLog('WAKE WORD DETECTED');
        setState('listening');
      }

      if (isAwake && lower && document.body.classList.contains('state-listening')) {
        const cmd = lower.replace(/kalki|jarvis/gi, '').trim();
        if (cmd) processCommand(cmd || transcript);
      }
    };

    recognition.onerror = (event) => addLog(`VOICE ERROR: ${event.error}`);

    recognition.onend = () => {
      if (document.body.classList.contains('state-listening') && !isAwake) setState('idle');
      isAwake = false;
    };
  }

  /* ─── Audio Init ─── */
  let audioCtx, analyzer;

  async function initAudio() {
    if (audioCtx) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyzer = audioCtx.createAnalyser();
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyzer);
      analyzer.fftSize = 128;
      window.__analyzer = analyzer;
      addLog('AUDIO SENSORS ACTIVE');
    } catch (err) {
      addLog('AUDIO ACCESS DENIED');
    }
  }

  /* ─── Command Processing ─── */
  async function processCommand(text) {
    setState('processing');
    addLog(`CMD: ${text.substring(0, 35)}...`);

    try {
      const response = await fetch('/api/v1/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: text, timestamp: new Date().toISOString() })
      });
      const data = await response.json();
      handleResponse(data.response);
    } catch (err) {
      addLog('ERROR: CONNECTION FAILED');
      setState('idle');
    }
  }

  function handleResponse(text) {
    const formatted = text.startsWith('Sir') || text.startsWith('sir') ? text : `Sir, ${text}`;
    setState('speaking');
    responseOverlay.innerText = formatted;
    responseOverlay.style.display = 'block';
    addLog('RESPONSE DELIVERED');

    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(formatted);
      utterance.rate = 0.95;
      utterance.pitch = 1.05;
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

  /* ─── Button Handlers ─── */
  document.getElementById('btnListen').addEventListener('click', async () => {
    if (recognition) {
      try {
        await initAudio();
        recognition.start();
        setState('listening');
        addLog('MANUAL ACTIVATION');
      } catch (e) {
        addLog('VOICE ENGINE RESTART');
      }
    } else {
      addLog('VOICE API NOT SUPPORTED - SIMULATING');
      setState('listening');
      setTimeout(() => {
        transcriptDisplay.innerText = 'Kalki, show system status';
        processCommand('show system status');
      }, 1500);
    }
  });

  document.getElementById('btnSimulate').addEventListener('click', () => {
    const commands = [
      'Kalki, run system diagnostics',
      'Kalki, check database status',
      'Kalki, what is today\'s date?',
      'Kalki, who are you?',
      'Kalki, what is the system uptime?'
    ];
    const cmd = commands[Math.floor(Math.random() * commands.length)];
    transcriptDisplay.innerText = cmd;
    processCommand(cmd);
  });

  /* ─── Keyboard Shortcuts ─── */
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !e.repeat && !e.target.matches('input, textarea')) {
      e.preventDefault();
      document.getElementById('btnListen').click();
    }
    if (e.code === 'Escape') {
      responseOverlay.style.display = 'none';
      setState('idle');
    }
  });

  /* ─── Topology SVG animation ─── */
  const topoSvg = document.getElementById('topologySvg');
  if (topoSvg) {
    let topoAngle = 0;
    setInterval(() => {
      topoAngle += 0.5;
      const nodes = topoSvg.querySelectorAll('.topo-node');
      nodes.forEach((node, i) => {
        const angle = (parseFloat(node.dataset.angle) || 0) + topoAngle;
        const rad = angle * Math.PI / 180;
        const r = 55;
        const cx = 100 + Math.cos(rad) * r;
        const cy = 75 + Math.sin(rad) * r;
        const circles = node.querySelectorAll('circle');
        if (circles.length >= 2) {
          circles[0].setAttribute('cx', cx);
          circles[0].setAttribute('cy', cy);
          circles[1].setAttribute('cx', cx);
          circles[1].setAttribute('cy', cy);
        }
      });
    }, 100);
  }

  addLog('HOLOGRAPHIC INTERFACE ACTIVE');

})();
