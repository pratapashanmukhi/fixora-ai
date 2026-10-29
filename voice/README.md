# FIXORA Voice Interaction Module

The Voice module provides microphone speech recognition, optional Gemini question answering with per-session diagnosis and conversation history, text input, and offline system text-to-speech. It is intended only for low-voltage educational circuits. Neither an image nor an AI response can verify circuit safety.

## Windows Setup

From the repository root, create and activate a virtual environment, then install the Voice dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r voice/packages.txt
```

If PyAudio installation fails, install a compatible wheel matching the Python version and system architecture. Microphone recognition uses Google's web recognition service and requires internet access, PyAudio, and a working microphone. `pyttsx3` uses the local Windows speech engine.

## API Key

Copy the safe template into a root-level `.env` file, then set your Gemini key:

```powershell
Copy-Item .env.example .env
```

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

The module also reads `GEMINI_API_KEY` from the process environment. Never commit `.env`; the repository ignore rules exclude it. Without a key, the assistant returns a safe notice instead of a Gemini answer.

## Run

From the repository root, start in automatic microphone mode (text mode is selected if the microphone is unavailable):

```powershell
py -m voice.voice_assistant_ai
```

Use text input directly:

```powershell
py -m voice.voice_assistant_ai --text
```

The standalone example uses explicitly labeled mock diagnosis data. Integrations may pass the Vision diagnosis dictionary and identify its source:

```python
from voice.voice_assistant_ai import main

main(diagnosis=diagnosis, diagnosis_source="ai_vision")
```

The dictionary may contain `status`, `fault_detected`, `fault_type`, `location`, `possible_cause`, `confidence`, and optional `bounding_box`. Set `diagnosis_source="mock"` for sample data; unknown provenance is not represented as an actual Vision result.

## Tests

Run the mocked Voice tests from the repository root:

```powershell
py -m unittest discover -s voice/tests -v
```

Tests do not access a live Gemini API, physical microphone, or speaker playback.