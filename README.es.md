# Content Toolkit

Herramientas de ingesta de contenido para el [Second Brain Ecosystem](https://github.com/Agents4Life/second-brain-ecosystem). Transforma medios (video, audio) en texto revisable antes de entrar al vault de Obsidian.

## Herramientas

| Herramienta | Descripción | Estado |
|------------|-------------|--------|
| [`transcribe/`](./transcribe/) | Transcripción de video/audio a texto con Whisper | 🟢 Listo |
| [`ingest-youtube/`](./ingest-youtube/) | Pipeline completo: YouTube → audio → transcripción → resumen inteligente → staging | 🟢 Listo |

## Pipeline de ingesta

```
YouTube URL  →  yt-dlp (audio)  →  Whisper (transcripción)  →  LLM (resumen)  →  staging
Video/Audio  →  ffmpeg (audio)  →  Whisper (transcripción)  →  staging
```

El output debe revisarse antes de entrar al pipeline de IA. Solo cuando el usuario decide que una fuente puede ser leída por IA, la mueve o copia a `raw/` dentro del vault. `raw/` es la frontera explícita de consentimiento para [Librarian](https://github.com/Agents4Life/librarian).

Flujo recomendado:

```text
content-toolkit → staging → revisión humana → raw/ → Librarian proposals → approve/apply → wiki/
```

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
├── ingest-youtube/   ← YouTube → transcripción + resumen → staging
├── transcribe/       ← Transcripción standalone de video/audio
└── README.md
```

## Autor

**Vanessa Pellegrini** — [vanp.dev](https://vanp.dev)
