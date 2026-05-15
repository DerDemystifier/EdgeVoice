# EdgeVoice

A desktop text-to-speech app built with [Flet](https://flet.dev/) and [`edge-tts`](https://github.com/rany2/edge-tts) for generating Microsoft Edge neural voices as MP3 files.

EdgeVoice gives you a clean GUI for:

- selecting a language, gender, and voice
- previewing voices before generating audio
- tuning rate, volume, and pitch
- generating a single MP3 with optional subtitles
- batch-generating multiple MP3 files from a text list
- saving your preferred theme and voice settings between sessions

> **Image placeholder:** add a hero screenshot at `docs/images/edgevoice-hero.png`

---

## Table of contents

- [Why EdgeVoice](#why-edgevoice)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output behavior](#output-behavior)
- [Troubleshooting](#troubleshooting)
- [Development notes](#development-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Why EdgeVoice

If you like the quality of Microsoft Edge voices but do **not** want to wrangle command-line flags every time, EdgeVoice wraps the workflow in a desktop UI that is quick to use and easy to revisit.

It is especially handy for:

- creating narration clips
- producing voice samples
- exporting dialogue lines in batches
- testing different voices and prosody settings
- generating MP3 + SRT output from a single interface

---

## Features

### Single generation

- Paste text or load it from a `.txt` file
- Choose an output `.mp3` path
- Optionally generate a matching `.srt` subtitle file
- Generate and immediately play the result in-app
- Stop playback from the UI

### Bulk generation

- Add rows manually
- Import a text file with **one entry per line**
- Edit or delete individual rows before generation
- Retry only failed rows
- Generate all pending rows into a selected output folder
- Track progress, completed item count, and estimated remaining time

### Voice workflow

- Load the Edge TTS voice catalog at startup
- Filter by locale/language and gender
- Preview the selected voice before committing to a full export
- Cache preview audio in the `samples/` folder for faster repeat previews

### Quality-of-life details

- Persist theme, voice, and prosody settings in `config.json`
- Light and dark mode toggle
- Desktop-native file and folder dialogs on Windows via `tkinter`
- Friendly status messages and snackbars for errors and success states

---

## Screenshots

Add these later when you are ready:

- **Hero image:** `docs/images/edgevoice-hero.png`
- **Single tab screenshot:** `docs/images/edgevoice-single-tab.png`
- **Bulk tab screenshot:** `docs/images/edgevoice-bulk-tab.png`
- **Voice preview / settings screenshot:** `docs/images/edgevoice-voice-panel.png`

Example snippet to enable later:

```md
![EdgeVoice main window](docs/images/edgevoice-hero.png)
```

---

## Tech stack

- **Python 3.11+**
- **Flet** — desktop UI
- **edge-tts** — voice synthesis
- **flet-audio** — in-app playback
- **tkinter** — native desktop open/save/folder dialogs

---

## Project structure

```text
EdgeVoice/
├─ main.py
├─ requirements.txt
├─ config.json
├─ samples/
├─ app/
│  ├─ app.py
│  ├─ constants.py
│  ├─ settings.py
│  ├─ state.py
│  ├─ tts.py
│  └─ ui/
│     ├─ bulk_tab.py
│     ├─ helpers.py
│     ├─ prosody_panel.py
│     ├─ single_tab.py
│     └─ voice_panel.py
└─ .github/
```

### File overview

- `main.py` — entry point that runs the Flet app
- `app/app.py` — page setup, theme handling, and top-level UI assembly
- `app/tts.py` — pure TTS helpers and synthesis logic
- `app/settings.py` — read/write persistence for user settings
- `app/state.py` — shared mutable app state
- `app/ui/single_tab.py` — single text generation workflow
- `app/ui/bulk_tab.py` — batch generation workflow
- `app/ui/voice_panel.py` — voice filtering and preview UI
- `app/ui/prosody_panel.py` — rate, volume, and pitch controls
- `app/ui/helpers.py` — shared UI helpers and file dialog wrappers
- `config.json` — persisted app preferences
- `samples/` — cached preview audio files

---

## Getting started

### Prerequisites

Make sure you have:

- Python 3.11 or newer
- a virtual environment tool such as `venv`
- internet access for `edge-tts` voice synthesis requests

### Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies from `requirements.txt`.

#### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run the app

```powershell
flet run main.py
```

or

```powershell
python main.py
```

If you already use the included virtual environment, activate it first and then run the app.

---

## Usage

### Single tab workflow

1. Launch the app.
2. Wait for the voice list to finish loading.
3. Choose a language, gender, and voice.
4. Adjust **Rate**, **Volume**, and **Pitch** if needed.
5. Enter text manually or load a `.txt` file.
6. Choose an output `.mp3` path.
7. Optionally enable subtitle export.
8. Click **Generate & Play** or **Save to File**.

### Bulk tab workflow

1. Open the **Bulk** tab.
2. Add rows manually or import a `.txt` file.
3. Choose an output folder.
4. Optionally enable subtitle export.
5. Click **Bulk Generate**.
6. Monitor the progress bar, completed count, and ETA.

---

## Configuration

EdgeVoice stores user preferences in `config.json`.

Currently persisted values include:

- theme mode
- selected language
- selected gender
- selected voice
- rate
- volume
- pitch

Example shape:

```json
{
  "gender": "Male",
  "language": "en-CA",
  "pitch": 0.0,
  "rate": 0.0,
  "theme": "light",
  "voice": "en-CA-LiamNeural",
  "vol": 0.0
}
```

---

## Output behavior

### Single generation

- Saves to the exact `.mp3` path you choose
- Optionally writes a sibling `.srt` file with the same base name

### Bulk generation

- Writes files to the selected output folder
- Uses numbered filenames in this format:

```text
001_<sanitized_text_prefix>.mp3
```

- File names are sanitized from the first part of each text entry
- Optional `.srt` files are generated alongside each `.mp3`
- A short cooldown is applied between items during batch generation

---

## Troubleshooting

### Voices do not load

- Check your internet connection
- Retry launching the app
- Confirm that `edge-tts` installed successfully in your environment

### Playback does not start

- Make sure the MP3 was generated successfully
- Try generating again with a short sample of text
- Check that the output path is writable

### File dialogs do not appear

On desktop, EdgeVoice uses native dialogs through `tkinter`. If dialogs fail:

- confirm your Python installation includes `tkinter`
- run the desktop app rather than a web deployment
- verify the environment is not heavily sandboxed

### Bulk generation stops on some rows

Failed rows remain marked with an error status. Use **Retry Errors** after adjusting inputs or re-running the app.

---

## Development notes

- Entry point: `main.py`
- App assembly happens in `app/app.py`
- TTS generation is async and handled in `app/tts.py`
- Voice previews are generated on demand and cached in `samples/`
- Desktop file and folder dialogs are wrapped in `app/ui/helpers.py`
- The app is designed primarily for desktop usage; web-mode save/folder flows are intentionally restricted

---

## Contributing

Issues, fixes, and polish improvements are welcome.

If you plan to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the app locally
5. Open a pull request with a clear description

A few good starter ideas:

- add screenshots and branding assets
- improve accessibility and keyboard flow
- add export presets
- add automated tests
- package the app for easier distribution

---

## License

No license file is currently included in this repository.
If you plan to publish or accept outside contributions, adding a license is a very good next move.
