# ingest-youtube

> YouTube → Audio → Transcription → Smart Summary → Obsidian

Pipeline completo para ingerir contenido de YouTube al vault de Obsidian.

## Requisitos

- `yt-dlp` (`brew install yt-dlp`)
- `ffmpeg` (`brew install ffmpeg`)
- `whisper` (`pip install openai-whisper`)
- Ollama corriendo localmente (para smart summary)

## Uso

```bash
# Básico
python ingest.py <youtube-url> <obsidian-dest-dir>

# Con opciones
python ingest.py <youtube-url> <obsidian-dest-dir> --model medium --lang en

# Sin resumen (solo transcripción)
python ingest.py <youtube-url> <obsidian-dest-dir> --no-summary

# Conservar audio
python ingest.py <youtube-url> <obsidian-dest-dir> --keep-audio
```

## Ejemplo

```bash
python ingest.py \
  "https://youtube.com/watch?v=kwSVtQ7dziU" \
  "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/second-brain-van-cp/raw/2-areas/01_dev_studio/05_IA" \
  --model medium --lang en
```

## Pipeline

```
1. yt-dlp descarga audio (best quality → WAV 16kHz mono)
2. Whisper transcribe (configurable: tiny/base/small/medium/large)
3. LLM genera smart summary (Ollama local)
4. Ambos .md se guardan en el destino de Obsidian
5. Audio temporal se elimina
```

## Output

Por cada video genera 2 archivos:
- `{slug}-transcripcion.md` — transcripción completa con metadata
- `{slug}-resumen.md` — resumen inteligente con temas clave + quotes

## Opciones

| Flag | Default | Descripción |
|------|---------|-------------|
| `--model` | `medium` | Modelo de Whisper (tiny/base/small/medium/large) |
| `--lang` | `en` | Idioma del audio |
| `--no-summary` | false | Saltar generación de resumen con LLM |
| `--keep-audio` | false | Conservar archivo de audio WAV |

## Environment

| Variable | Default | Descripción |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434/v1` | Endpoint del LLM |
| `OLLAMA_MODEL` | `qwen3.5:4b` | Modelo para resumen |
