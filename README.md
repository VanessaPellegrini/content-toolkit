# Content Toolkit

<img src="https://img.shields.io/badge/transcribe-ready-green" alt="transcribe" /> <img src="https://img.shields.io/badge/ingest_youtube-ready-green" alt="ingest-youtube" />

Tools for content creators. Turn video and audio into text — transcribe with Whisper, extract YouTube content end-to-end with yt-dlp, and generate smart summaries with local LLMs. Everything stages for human review before entering your Obsidian vault.

Part of the [Second Brain Ecosystem](https://github.com/Agents4Life/second-brain-ecosystem).

## Tools

| Tool | Description | Status |
|------|-------------|--------|
| [`transcribe/`](./transcribe/) | Video/audio transcription to text with Whisper | 🟢 Ready |
| [`ingest-youtube/`](./ingest-youtube/) | Full pipeline: YouTube → audio → transcription → smart summary → staging | 🟢 Ready |

## Ingestion Pipeline

```
YouTube URL  →  yt-dlp (audio)  →  Whisper (transcription)  →  LLM (summary)  →  staging
Video/Audio  →  ffmpeg (audio)  →  Whisper (transcription)  →  staging
```

Output must be reviewed before entering the AI pipeline. Only when the user decides a source can be read by AI, they move or copy it to `raw/` inside the vault. `raw/` is the explicit consent boundary for [Librarian](https://github.com/Agents4Life/librarian).

Recommended flow:

```text
content-toolkit → staging → human review → raw/ → Librarian proposals → approve/apply → wiki/
```

## Setup

Each tool has its own `README.md` with installation and usage instructions.

### General Requirements

- Python 3
- `ffmpeg` (`brew install ffmpeg`)
- `whisper` (`pip install openai-whisper`)
- [Ollama](https://ollama.ai) running locally (for smart summaries)

## Structure

```
content-toolkit/
├── ingest-youtube/   ← YouTube → transcription + summary → staging
├── transcribe/       ← Standalone video/audio transcription
└── README.md
```

## Author

**Vanessa Pellegrini** — [vanp.dev](https://vanp.dev)
