import os
import time
import subprocess
import glob
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from google import genai
import database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB asynchronously on startup
    await database.init_db()
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

Work Management Capabilities:
1. Tasks: You can manage a mission log.
2. Files: You can navigate and organize the user's workspace.
3. Email: You can draft and simulate communications.
"""

class CommandRequest(BaseModel):
    command: str
    timestamp: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"

@app.post("/api/v1/command")
async def handle_command(req: CommandRequest):
    start_time = time.time()
    transcript = req.command

    # Intention Engine
    response_text = ""
    intent = "chat"
    cmd_lower = transcript.lower()

    # --- Work Management Intention Logic ---

    # 1. Task Management
    if any(word in cmd_lower for word in ["task", "mission", "to do", "todo"]):
        if any(word in cmd_lower for word in ["add", "create", "new", "record"]):
            intent = "task_add"
            # Basic extraction
            if "add task" in cmd_lower: title = transcript.split("add task")[-1].strip()
            elif "create mission" in cmd_lower: title = transcript.split("create mission")[-1].strip()
            elif "new task" in cmd_lower: title = transcript.split("new task")[-1].strip()
            else: title = transcript.replace("task", "").replace("mission", "").strip()

            if not title: title = "Unspecified Mission"
            await database.add_task(title)
            response_text = f"The mission has been recorded in the log, sir: {title}"
        elif any(word in cmd_lower for word in ["list", "show", "get"]):
            intent = "task_list"
            tasks = await database.get_tasks()
            if tasks:
                task_str = "\n".join([f"- {t[1]} [{t[3]}]" for t in tasks])
                response_text = f"Displaying current missions, sir:\n{task_str}"
            else:
                response_text = "The mission log is currently clear, sir."
        else:
            intent = "task_query"
            response_text = "How shall I manage your missions today, sir?"

    # 2. File Management
    elif any(word in cmd_lower for word in ["file", "directory", "folder", "archive", "workspace"]):
        intent = "files"
        if any(word in cmd_lower for word in ["list", "show", "browse"]):
            files = os.listdir('.')
            files_str = ", ".join(files[:20])
            response_text = f"Scanning directory, sir. Found: {files_str}"
        elif any(word in cmd_lower for word in ["search", "find", "locate"]):
            query = transcript.split("find")[-1].strip() if "find" in cmd_lower else transcript.split("search")[-1].strip()
            if not query or query == transcript: query = "*"
            found = [f for f in glob.glob(f"**/*{query}*", recursive=True) if os.path.isfile(f)]
            if found:
                files_found = ", ".join(found[:5])
                response_text = f"Archives searched, sir. Located {len(found)} relevant files, including: {files_found}"
            else:
                response_text = "My search of the archives yielded no results, sir."
        else:
            response_text = "Archive access established, sir. What is your command regarding the workspace?"

    # 3. Email Management
    elif any(word in cmd_lower for word in ["mail", "email", "message"]):
        intent = "mail"
        if "draft" in cmd_lower or "write" in cmd_lower:
            response_text = "I have prepared a draft with appropriate tone and precision, sir. Shall I read it back?"
        else:
            response_text = "Communication core online, sir. Checking for incoming messages... No urgent dispatches at this time."

    # 4. Standard Diagnostics (Existing)
    elif "system diagnostics" in cmd_lower:
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

    # AI Fallback for complex requests
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
    await database.log_command(transcript, intent, response_text, duration)

    return {
        "status": "success",
        "intent": intent,
        "response": response_text,
        "duration": f"{duration:.4f}s"
    }

# Dedicated Task API
@app.get("/api/v1/tasks")
async def list_tasks(status: str = None):
    tasks = await database.get_tasks(status)
    return {"tasks": [{"id": t[0], "title": t[1], "description": t[2], "status": t[3], "priority": t[4], "created_at": t[5]} for t in tasks]}

@app.post("/api/v1/tasks")
async def create_task(task: TaskCreate):
    await database.add_task(task.title, task.description, task.priority)
    return {"status": "task created"}

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
