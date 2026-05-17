# Content Toolkit

Herramientas de ingesta de contenido para el [Second Brain Ecosystem](https://github.com/Agents4Life/second-brain-ecosystem). Transforma medios (video, audio) en texto listo para tu vault de Obsidian.

## Herramientas

| Herramienta | Descripción | Estado |
|------------|-------------|--------|
| [`transcribe/`](./transcribe/) | Transcripción de video/audio a texto con Whisper | 🟢 Listo |
| [`ingest-youtube/`](./ingest-youtube/) | Pipeline completo: YouTube → audio → transcripción → resumen inteligente → Obsidian | 🟢 Listo |

## Pipeline de ingesta

```
YouTube URL  →  yt-dlp (audio)  →  Whisper (transcripción)  →  LLM (resumen)  →  raw/ (vault)
Video/Audio  →  ffmpeg (audio)  →  Whisper (transcripción)  →  raw/ (vault)
```

Todo el contenido procesado va a la carpeta `raw/` del vault de Obsidian, donde [Librarian](https://github.com/Agents4Life/librarian) puede curarlo e integrarlo al wiki.

## Setup

Cada herramienta tiene su propio `README.md` con instrucciones de instalación y uso.

### Requisitos generales

- Python 3
- `ffmpeg` (`brew install ffmpeg`)
- `whisper` (`pip install openai-whisper`)
- [Ollama](https://ollama.ai) corriendo localmente (para resúmenes inteligentes)

## Estructura

```
content-toolkit/
├── ingest-youtube/   ← YouTube → transcripción + resumen → Obsidian
├── transcribe/       ← Transcripción standalone de video/audio
└── README.md
```

## Autor

**Vanessa Pellegrini** — [vanp.dev](https://vanp.dev)
