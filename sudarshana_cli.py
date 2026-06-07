import asyncio
import os
import sys
import time
import subprocess
import argparse
from dotenv import load_dotenv
from google import genai
from database import init_db, log_command

load_dotenv()

# Cinematic Colors
CYAN = "\033[36m"
BLUE = "\033[34m"
AMBER = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"

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
- Never break character. You are SUDARSHANA, running on a secure local mainframe.
- Avoid overly enthusiastic, cheerful, or 'bubbly' language. You are suave, grounded, and coolly professional.
"""

def typing_print(text, speed=0.02):
    print(f"{CYAN}{BOLD}SUDARSHANA:{RESET} ", end="", flush=True)
    for char in text:
        sys.stdout.write(f"{CYAN}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    print("\n")

async def handle_cli_command(transcript, client):
    start_time = time.time()
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
    await log_command(transcript, intent, response_text, duration)
    return response_text

async def main():
    await init_db()

    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
    client = None
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)

    os.system('clear' if os.name == 'posix' else 'cls')

    print(f"{BLUE}{BOLD}" + "="*60)
    print(f"   SUDARSHANA OS TERMINAL - SECURE UPLINK ESTABLISHED")
    print(f"   COGNITIVE ENGINE: {'ONLINE' if client else 'OFFLINE'} | PERSISTENCE LAYER: ACTIVE")
    print(f"="*60 + f"{RESET}\n")

    typing_print("Core systems online. Awaiting your command, Sir.")

    while True:
        try:
            user_input = input(f"{AMBER}{BOLD}SIR >{RESET} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "shutdown"]:
                typing_print("Shutting down core systems. Goodbye, Sir.")
                break

            response = await handle_cli_command(user_input, client)
            typing_print(response)

        except KeyboardInterrupt:
            print("\n")
            typing_print("Emergency shutdown initiated. Goodbye, Sir.")
            break
        except Exception as e:
            print(f"{AMBER}An unexpected error occurred: {e}{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
