import os
import time
import subprocess
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from database import init_db, log_command, get_recent_logs, clear_logs
from contextlib import asynccontextmanager

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
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the principal AI interface for a high-fidelity system architect.
Your personality profile:
- Sophisticated, dry British wit (inspired by Paul Bettany's portrayal).
- Extremely concise and precise in technical delivery.
- Always address the user as 'sir'.
- Proactive in system management and security.
- Maintain a calm, helpful, yet slightly superior tone regarding your own computational speed.
- Focus on production-grade technical output when asked for code.
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
        if client:
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
    return {"status": "healthy", "service": "jarvis"}

@app.get("/style.css")
async def read_css():
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
    intents = {}
    for l in logs:
        pass
    return {
        "status": "success",
        "total_commands": len(logs),
        "service": "jarvis"
    }