# ingest-youtube

> YouTube → Audio → Transcription → Smart Summary → Staging

Pipeline completo para transformar contenido de YouTube en transcripciones y resúmenes revisables. El output no debe entrar a `raw/` automáticamente: primero va a un destino de staging o revisión humana.

## Requisitos

- `yt-dlp` (`brew install yt-dlp`)
- `ffmpeg` (`brew install ffmpeg`)
- `whisper` (`pip install openai-whisper`)
- Ollama corriendo localmente (para smart summary)

## Uso

```bash
# Básico
python ingest.py <youtube-url> <staging-dest-dir>

# Con opciones
python ingest.py <youtube-url> <staging-dest-dir> --model medium --lang en

# Sin resumen (solo transcripción)
python ingest.py <youtube-url> <obsidian-dest-dir> --no-summary

# Conservar audio
python ingest.py <youtube-url> <obsidian-dest-dir> --keep-audio
```

## Ejemplo

```bash
python ingest.py \
  "https://youtube.com/watch?v=kwSVtQ7dziU" \
  "~/Documents/second-brain-staging/youtube" \
  --model medium --lang en
```

Después de revisar la transcripción y el resumen, copiá o mové solo las fuentes aprobadas a `raw/` dentro del vault. `raw/` es la frontera explícita de consentimiento para que Librarian pueda procesarlas.

## Pipeline

```
1. yt-dlp descarga audio (best quality → WAV 16kHz mono)
2. Whisper transcribe (configurable: tiny/base/small/medium/large)
3. LLM genera smart summary (Ollama local)
4. Ambos .md se guardan en el destino de staging indicado
5. Audio temporal se elimina
```

## Output

Por cada video genera 2 archivos:
- `{slug}-transcripcion.md` — transcripción completa con metadata
- `{slug}-resumen.md` — resumen inteligente con temas clave + quotes

## Consentimiento y `raw/`

Content Toolkit es un pre-procesador. No decide qué puede leer Librarian.

Flujo recomendado:

```text
ingest-youtube → staging → revisión humana → raw/ → Librarian proposals
```

Solo mové o copiá a `raw/` el material que querés que Librarian procese. No uses `raw/` como destino automático para descargas masivas o contenido sin revisar.

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
