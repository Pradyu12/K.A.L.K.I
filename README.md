# J.A.R.V.I.S. High-Fidelity System

A futuristic, highly asynchronous J.A.R.V.I.S. system featuring a cinematic HUD and a Python-based intelligent backend.

## Features

- **Holographic HUD**: Built with Vanilla JS, HTML5, and CSS3. Features an animated Arc Reactor, glass-morphism panels, and live telemetry simulations.
- **Intelligent Backend**: FastAPI-powered server with an asynchronous "Intention Engine".
- **AI Integration**: Seamless fallback to Google Gemini AI for natural conversation, using the `google-genai` SDK.
- **Persistence**: Non-blocking SQLite storage via `aiosqlite` for command logging and session memory.
- **Voice Interface**: Native Web Speech API integration with wake-word detection ("Jarvis").

## Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn google-genai aiosqlite
   ```

2. **Configure API Key**:
   Set your Google AI API key as an environment variable:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Run the Server**:
   ```bash
   python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the HUD**:
   Open `http://localhost:8000` in a modern web browser (Chrome/Edge recommended for Speech API support).

## Project Structure

- `backend/`: FastAPI application and database logic.
- `frontend/`: Cinematic HUD assets, styles, and logic.
- `frontend/assets/`: SVG icons and branding.

## License
MIT
