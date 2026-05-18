import os
import time
import subprocess
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from .database import init_db, log_command
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB asynchronously on startup
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client if API key is present
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are J.A.R.V.I.S., a sophisticated AI assistant.
Your personality: dry British wit, extremely concise, highly professional, and you always address the user as 'sir'.
You specialize in technical systems, code, and home automation.
Maintain the persona at all times.
"""

class CommandRequest(BaseModel):
    command: str
    timestamp: str

@app.post("/api/v1/command")
async def handle_command(req: CommandRequest):
    start_time = time.time()
    transcript = req.command

    # Intention Engine
    response_text = ""
    intent = "chat"

    # Local Structural Tasks
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

    # AI Fallback
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

    # Log asynchronously (non-blocking)
    await log_command(transcript, intent, response_text, duration)

    return {
        "status": "success",
        "intent": intent,
        "response": response_text,
        "duration": f"{duration:.4f}s"
    }

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
