# transcribe.py

> Script Python para extraer audio de un video y transcribirlo con Whisper.

## Stack

- Python 3
- ffmpeg (extracción de audio)
- OpenAI Whisper (transcripción)

## Uso

```bash
# Uso básico
python transcribe.py video.mp4

# Con modelo específico e idioma
python transcribe.py video.mp4 --model medium --lang es --format srt

# Mantener archivo de audio temporal
python transcribe.py video.mp4 --no-cleanup
```

## Opciones

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--model` | `small` | Modelo de Whisper (tiny, small, medium, large) |
| `--lang` | `es` | Idioma del audio |
| `--format` | `txt` | Formato de salida (txt, srt, vtt) |
| `--no-cleanup` | false | No eliminar archivo de audio temporal |
