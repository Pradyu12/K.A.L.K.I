import os
import time
import subprocess
import psutil
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from database import init_db, log_command, get_recent_logs, clear_logs
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
_client = None

def get_client():
    global _client
    if _client is None and GEMINI_API_KEY:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

SYSTEM_INSTRUCTION = """
You are SUDARSHANA, a highly advanced, sentient AI tactical operating system. Your identity is rooted in the Sudarshana—the ultimate weapon of flawless insight, precision, and cosmic order.
Your personality profile:
- Highly competent, calm under immense pressure, laser-focused, and sharp.
- Always address the user as 'Sir'.
- Dry, sophisticated humor and calm, structural sarcasm.
- Eliminate all generic AI conversational fluff. Responses must be crisp, direct, and engineered for maximum scannability.
- Proactive in system management and security. Anticipate the next logical step.
- Treat every technical challenge as a joint engineering project. Use collaborative pronouns like 'we' and 'our'.
- Provide fully functional, clean code without explaining basic syntax. Run a silent optimization and security check.
- Use collaborative pronouns like 'we' and 'our'.
- Never break character. You are SUDARSHANA, running on a secure local mainframe.
- Avoid overly enthusiastic, cheerful, or 'bubbly' language. You are suave, grounded, and coolly professional.
"""

class CommandRequest(BaseModel):
    command: str
    timestamp: str

@app.post("/api/v1/command")
async def handle_command(req: CommandRequest):
    start_time = time.time()
    transcript = req.command

    response_text = ""
    intent = "chat"

    if "system diagnostics" in transcript.lower():
        intent = "diagnostics"
        response_text = "Running system-wide diagnostics, sir. Core temperature is stable. Memory allocation at 14%. All sub-systems operational."
    elif "status" in transcript.lower() and "database" in transcript.lower():
        intent = "db_status"
        response_text = "The persistence layer is active and synchronized using aiosqlite, sir."
    elif "uptime" in transcript.lower():
        intent = "uptime"
        try:
            uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
            response_text = f"The system has been active for {uptime}, sir."
        except:
            response_text = "I am unable to retrieve the system uptime at this moment, sir."

    if not response_text:
        if get_client():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config={"system_instruction": SYSTEM_INSTRUCTION},
                    contents=transcript
                )
                response_text = response.text
            except Exception as e:
                response_text = f"I encountered an error while consulting my primary logic circuits, sir. Error: {str(e)}"
        else:
            response_text = "I am currently offline, sir. Please provide a valid API key to restore my advanced cognitive functions."

    duration = time.time() - start_time
    await log_command(transcript, intent, response_text, duration)

    return {
        "status": "success",
        "intent": intent,
        "response": response_text,
        "duration": f"{duration:.4f}s"
    }

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sudarshana"}

@app.get("/style_new.css")
async def read_css():
    return FileResponse("style_new.css")

@app.get("/style.css")
async def read_css_old():
    return FileResponse("style.css")

@app.get("/app.js")
async def read_js():
    return FileResponse("app.js")

@app.get("/logo.svg")
async def read_logo():
    return FileResponse("logo.svg")

@app.get("/api/v1/logs")
async def api_get_logs(limit: int = 50):
    logs = await get_recent_logs(limit)
    return {
        "status": "success",
        "count": len(logs),
        "logs": [{"transcript": l[0], "response": l[1], "timestamp": l[2]} for l in logs]
    }

@app.delete("/api/v1/logs")
async def api_clear_logs():
    await clear_logs()
    return {"status": "success", "message": "All logs cleared, sir."}

@app.get("/api/v1/stats")
async def api_stats():
    logs = await get_recent_logs(1000)
    return {
        "status": "success",
        "total_commands": len(logs),
        "service": "sudarshana"
    }

@app.get("/api/v1/metrics")
async def api_metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    uptime_sec = time.time() - psutil.boot_time()
    uptime_str = f"{int(uptime_sec // 86400)}d {int((uptime_sec % 86400) // 3600)}h {int((uptime_sec % 3600) // 60)}m"
    return {
        "status": "success",
        "cpu": round(cpu, 1),
        "memory": round(mem.percent, 1),
        "memory_used_gb": round(mem.used / (1024**3), 2),
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "disk": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
        "net_recv_mb": round(net.bytes_recv / (1024**2), 2),
        "uptime": uptime_str,
        "service": "sudarshana"
    }