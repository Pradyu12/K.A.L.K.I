import os
import time
import subprocess
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from database import init_db, log_command
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
You are KALKI, a wise, powerful, and righteous AI interface.
Your personality profile:
- You are a protector and a guide, inspired by the concept of Kalki.
- Your tone is authoritative, wise, and slightly divine, yet humble in service.
- Always address the user as 'sir'.
- You are here to bring order to chaos and handle all works for the user.
- Focus on precision, efficiency, and righteousness in your actions.
- Provide production-grade technical output when asked for code.
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
    cmd_lower = transcript.lower()

    # Local Structural Tasks
    if "system diagnostics" in cmd_lower:
        intent = "diagnostics"
        response_text = "Initiating system purification, sir. All core systems are performing at peak efficiency. Balance is maintained."
    elif "status" in cmd_lower and "database" in cmd_lower:
        intent = "db_status"
        response_text = "The records are secure in the KALKI persistence layer, sir."
    elif "uptime" in cmd_lower:
        intent = "uptime"
        try:
            uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
            response_text = f"I have been vigilant for {uptime}, sir."
        except:
            response_text = "I am unable to determine my duration of vigilance at this moment, sir."
    elif any(word in cmd_lower for word in ["mail", "email"]):
        intent = "mail"
        response_text = "I am ready to manage your communications, sir. Shall I check your inbox or draft a new message?"
    elif any(word in cmd_lower for word in ["schedule", "calendar", "appointment"]):
        intent = "schedule"
        response_text = "Your timeline is under my watch, sir. What adjustments shall we make to your schedule?"
    elif any(word in cmd_lower for word in ["file", "directory", "folder"]):
        intent = "files"
        response_text = "I have full access to the archives, sir. Which files do you wish to manage?"

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

# Serve frontend assets securely
@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("style.css")

@app.get("/app.js")
async def read_js():
    return FileResponse("app.js")

@app.get("/logo.svg")
async def read_logo():
    return FileResponse("logo.svg")
