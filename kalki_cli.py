import asyncio
import os
import sys
import time
import subprocess
import glob
from google import genai
import database

# Cinematic Colors - KALKI Theme (Gold, Saffron, Purple)
GOLD = "\033[33m"
SAFFRON = "\033[38;5;208m"
PURPLE = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

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

def typing_print(text, speed=0.01):
    print(f"{GOLD}{BOLD}KALKI:{RESET} ", end="", flush=True)
    for char in text:
        sys.stdout.write(f"{GOLD}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    print("\n")

async def handle_cli_command(transcript, client):
    start_time = time.time()
    response_text = ""
    intent = "chat"
    cmd_lower = transcript.lower()

    # --- Work Management Intention Logic ---
    if any(word in cmd_lower for word in ["task", "mission", "to do", "todo"]):
        if any(word in cmd_lower for word in ["add", "create", "new"]):
            intent = "task_add"
            title = transcript.split("add task")[-1].strip() if "add task" in cmd_lower else transcript
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
            response_text = "How shall I manage your missions today, sir?"

    elif any(word in cmd_lower for word in ["file", "directory", "folder", "list files"]):
        intent = "files"
        if "list" in cmd_lower:
            files = os.listdir('.')
            files_str = ", ".join(files[:15])
            response_text = f"Scanning directory, sir. Found: {files_str}"
        elif "search" in cmd_lower or "find" in cmd_lower:
            query = transcript.split("find")[-1].strip()
            found = glob.glob(f"**/*{query}*", recursive=True)
            response_text = f"Archives searched, sir. Located {len(found)} relevant files."
        else:
            response_text = "Archive access established, sir."

    elif any(word in cmd_lower for word in ["mail", "email"]):
        intent = "mail"
        response_text = "Communication core online, sir. No urgent dispatches found."

    elif "system diagnostics" in cmd_lower:
        intent = "diagnostics"
        response_text = "Initiating system purification, sir. All core systems are performing at peak efficiency."
    elif "uptime" in cmd_lower:
        intent = "uptime"
        try:
            uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
            response_text = f"I have been vigilant for {uptime}, sir."
        except:
            response_text = "I am currently vigilant, sir."

    elif any(word in cmd_lower for word in ["open", "launch", "start"]):
        intent = "system_control"
        if "browser" in cmd_lower or "chrome" in cmd_lower:
            if sys.platform == "linux":
                subprocess.Popen(["xdg-open", "https://google.com"])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "https://google.com"])
            response_text = "Launching the web browser for your research, sir."
        elif "code" in cmd_lower or "editor" in cmd_lower or "vs code" in cmd_lower:
            subprocess.Popen(["code", "."])
            response_text = "Opening your development environment, sir."
        else:
            response_text = "Which system component shall I initialize for you, sir?"

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
                response_text = f"I encountered an error, sir. Error: {str(e)}"
        else:
            response_text = "I am currently offline, sir. Advanced cognition requires an API key."

    duration = time.time() - start_time
    await database.log_command(transcript, intent, response_text, duration)
    return response_text

async def main():
    await database.init_db()

    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
    client = None
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)

    os.system('clear' if os.name == 'posix' else 'cls')

    print(f"{PURPLE}{BOLD}" + "="*60)
    print(f"   KALKI TERMINAL INTERFACE - SECURE UPLINK ESTABLISHED")
    print(f"   PERSISTENCE LAYER: ACTIVE | COGNITIVE ENGINE: JULES_LOCAL_V4.05")
    print(f"="*60 + f"{RESET}\n")

    typing_print("The age of chaos ends, sir. KALKI is online and ready for your command.")

    while True:
        try:
            user_input = input(f"{SAFFRON}{BOLD}SIR >{RESET} ").strip()
            if not user_input: continue
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                typing_print("Shutting down core systems. Have a pleasant evening, sir.")
                break
            response = await handle_cli_command(user_input, client)
            typing_print(response)
        except KeyboardInterrupt:
            print("\n")
            typing_print("Emergency shutdown initiated. Goodbye, sir.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
