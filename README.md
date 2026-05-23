# KALKI: The Righteous Work Assistant

KALKI is a wise, powerful, and righteous AI interface designed to bring order to your digital life and manage your work with precision.

## Core Features

- **Mission Log**: Comprehensive task management system. KALKI tracks your objectives and ensures you stay focused on what's important.
- **Archive Management**: Intelligent file browsing and organization. KALKI can scan your workspaces and locate crucial data.
- **Communication Core**: Streamlined email drafting and communication management.
- **Cinematic HUD**: A futuristic, high-fidelity browser-based interface for voice and visual interaction.
- **Terminal Uplink**: A robust CLI for advanced command-line interaction.
- **Cognitive Engine**: Powered by Google Gemini AI for deep understanding and natural conversation.

## Personality Profile

KALKI is more than a tool; it is a guide. Inspired by the concept of the final avatar, KALKI seeks to restore balance to your workflow.
- **Tone**: Authoritative, wise, and divine.
- **Language**: Always addresses the user as 'sir'.
- **Focus**: Efficiency, righteousness, and order.

## Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn google-genai aiosqlite
   ```

2. **Configure AI Engine**:
   Set your Google AI API key as an environment variable:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Run the Backend**:
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the HUD**:
   Open `http://localhost:8000` in a modern web browser.

5. **Terminal Access**:
   ```bash
   python3 kalki_cli.py
   ```

## Project Structure

- `main.py`: The FastAPI backend and intention engine.
- `database.py`: Persistence layer for missions and settings.
- `index.html`, `style.css`, `app.js`: The cinematic HUD frontend.
- `kalki_cli.py`: The command-line interface.
- `logo.svg`: The stylized KALKI emblem.
- `kalki_core.db`: The SQLite database (generated on first run).
