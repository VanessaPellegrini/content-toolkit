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

## Output y Consentimiento

Por defecto, el script escribe la transcripción junto al archivo de video/audio de entrada. Usá ese resultado como staging: revisalo antes de copiarlo o moverlo al vault.

En el Second Brain Ecosystem, `raw/` es la frontera explícita de consentimiento para procesamiento con IA. Librarian solo debe leer fuentes que el usuario decidió mover o copiar a `raw/`.

Flujo recomendado:

```text
transcribe → staging/local output → revisión humana → raw/ → Librarian proposals
```

No uses `raw/` como destino automático para transcripciones sin revisar.

## Opciones

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--model` | `small` | Modelo de Whisper (tiny, small, medium, large) |
| `--lang` | `es` | Idioma del audio |
| `--format` | `txt` | Formato de salida (txt, srt, vtt) |
| `--no-cleanup` | false | No eliminar archivo de audio temporal |
