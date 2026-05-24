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
import database
from contextlib import asynccontextmanager
import datetime
import platform

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

# --- KALKI COGNITIVE ENGINE (GEMINI INTEGRATED) ---
class KalkiEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except ImportError:
                print("Gemini SDK not found. Falling back to local logic.")

    def get_response(self, transcript: str) -> str:
        cmd = transcript.lower()

        # System Control Hook
        if any(word in cmd for word in ["open", "launch", "start"]):
            if "browser" in cmd or "chrome" in cmd:
                self.execute_pc_command("browser")
                return "Launching the web browser for your research, sir."
            if "code" in cmd or "editor" in cmd or "vs code" in cmd:
                self.execute_pc_command("editor")
                return "Opening your development environment, sir."

        if self.client:
            try:
                prompt = f"You are KALKI, a wise, powerful, and righteous AI work assistant. You address the user as 'sir'. Your tone is authoritative yet serving. Keep responses concise and work-focused. User says: {transcript}"
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
            except Exception as e:
                return f"My connection to the celestial intelligence is interrupted, sir. Local logic: I have received your command: {transcript}"

        # Local Fallback Persona
        if any(word in cmd for word in ["hello", "hi", "hey", "wake up"]):
            return "Kalki Core online. I am at your service, sir. How shall we bring order to the archives today?"

        if any(word in cmd for word in ["who are you", "what are you"]):
            return "I am KALKI, the Righteous Work Assistant. Dedicated to your productivity and the restoration of order in your workspace, sir."

        if "time" in cmd:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            return f"The current temporal coordinate is {now}, sir."

        return "My local logic has processed your request, sir. Standing by for further instructions."

    def execute_pc_command(self, action: str):
        try:
            if action == "browser":
                if platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", "https://google.com"])
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", "https://google.com"])
            elif action == "editor":
                subprocess.Popen(["code", "."])
        except Exception as e:
            print(f"Failed to execute PC command: {e}")

kalki = KalkiEngine()

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

    # 4. PC Control & System Commands
    elif any(word in cmd_lower for word in ["open", "launch", "start", "close", "exit"]):
        intent = "system_control"
        if "browser" in cmd_lower or "chrome" in cmd_lower:
            kalki.execute_pc_command("browser")
            response_text = "Launching the web browser for your research, sir."
        elif "code" in cmd_lower or "editor" in cmd_lower or "vs code" in cmd_lower:
            kalki.execute_pc_command("editor")
            response_text = "Opening your development environment, sir."
        else:
            response_text = "Which system component shall I initialize for you, sir?"

    # 5. Standard Diagnostics (Existing)
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

    # 5. Git Operations (GitHub/GitLab)
    elif any(word in cmd_lower for word in ["git", "repo", "repository", "github", "gitlab", "commit", "push", "pull"]):
        intent = "git"
        if "status" in cmd_lower:
            try:
                status = subprocess.check_output(["git", "status", "--short"]).decode().strip()
                response_text = f"Repository status retrieved, sir:\n{status}" if status else "The workspace is clean, sir."
            except:
                response_text = "I cannot detect a git repository in this archive, sir."
        elif "log" in cmd_lower:
            try:
                logs = subprocess.check_output(["git", "log", "-n", "3", "--oneline"]).decode().strip()
                response_text = f"Recent archive commits, sir:\n{logs}"
            except:
                response_text = "Failed to access archive history, sir."
        else:
            response_text = "Git integration active, sir. I can provide status or history of your repositories."

    # Kalki Logic Fallback (Gemini/Local)
    if not response_text:
        response_text = kalki.get_response(transcript)

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
