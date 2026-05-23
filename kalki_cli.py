import asyncio
import os
import sys
import time
import subprocess
import argparse
from google import genai
from database import init_db, log_command

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
"""

def typing_print(text, speed=0.02):
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
    await log_command(transcript, intent, response_text, duration)
    return response_text

async def main():
    await init_db()

    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
    client = None
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)

    os.system('clear' if os.name == 'posix' else 'cls')

    print(f"{PURPLE}{BOLD}" + "="*60)
    print(f"   KALKI TERMINAL INTERFACE - SECURE UPLINK ESTABLISHED")
    print(f"   PERSISTENCE LAYER: ACTIVE | COGNITIVE ENGINE: {'ONLINE' if client else 'OFFLINE'}")
    print(f"="*60 + f"{RESET}\n")

    typing_print("The age of chaos ends, sir. KALKI is online and ready for your command.")

    while True:
        try:
            user_input = input(f"{SAFFRON}{BOLD}SIR >{RESET} ").strip()

            if not user_input:
                continue

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
            print(f"{AMBER}An unexpected error occurred: {e}{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
