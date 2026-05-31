# Content Toolkit

Content ingestion tools for the [Second Brain Ecosystem](https://github.com/Agents4Life/second-brain-ecosystem). Transforms media (video, audio) into reviewable text before it enters the Obsidian vault.

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
