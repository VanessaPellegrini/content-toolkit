#!/usr/bin/env python3
"""
transcribe.py — Extrae audio de un video y lo transcribe con Whisper.

Uso:
    python transcribe.py video.mp4
    python transcribe.py video.mp4 --model medium --lang es --format srt
    python transcribe.py video.mp4 --no-cleanup    # keep audio.wav
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(video_path: str, output_path: str) -> None:
    """Extrae audio como WAV 16kHz mono usando ffmpeg."""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # sin video
        "-acodec", "pcm_s16le",   # WAV raw
        "-ar", "16000",           # 16kHz
        "-ac", "1",               # mono
        "-y",                     # sobreescribir
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[OK] Audio extraído: {output_path}")


def transcribe(audio_path: str, model_name: str, language: str) -> dict:
    """Transcribe audio con Whisper y devuelve el resultado."""
    import whisper
    print(f"Cargando modelo '{model_name}'...")
    model = whisper.load_model(model_name)
    print("Transcribiendo...")
    result = model.transcribe(audio_path, language=language, verbose=False)
    return result


def save_transcription(result: dict, output_dir: str, base_name: str, fmt: str) -> list[str]:
    """Guarda la transcripción en el formato solicitado. Retorna paths creados."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    text = result["text"]

    if fmt == "txt":
        path = output_dir / f"{base_name}.txt"
        path.write_text(text.strip(), encoding="utf-8")
        saved.append(str(path))

    elif fmt == "srt":
        path = output_dir / f"{base_name}.srt"
        lines = []
        for i, seg in enumerate(result["segments"], 1):
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(seg["text"].strip())
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(str(path))

    elif fmt == "all":
        # txt
        txt_path = output_dir / f"{base_name}.txt"
        txt_path.write_text(text.strip(), encoding="utf-8")
        saved.append(str(txt_path))

        # srt
        srt_path = output_dir / f"{base_name}.srt"
        lines = []
        for i, seg in enumerate(result["segments"], 1):
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(seg["text"].strip())
            lines.append("")
        srt_path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(str(srt_path))

        # json (full)
        import json
        json_path = output_dir / f"{base_name}.json"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        saved.append(str(json_path))

    return saved


def _format_timestamp(seconds: float) -> str:
    """Formatea segundos a HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def get_duration(video_path: str) -> float:
    """Retorna duración del video en segundos."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio de un video usando Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modelos disponibles (de más rápido a más preciso):
  tiny    ~39M    — muy rápido, aceptable
  base    ~74M    — rápido, bueno
  small   ~244M   — medio, muy bueno
  medium  ~769M   — lento, excelente (recomendado para español)
  large   ~1550M  — muy lento, SOTA

Formatos:
  txt   — texto plano
  srt   — subtítulos con timestamps
  all   — txt + srt + json completo
        """,
    )
    parser.add_argument("video", help="Ruta al archivo de video (mp4, mkv, webm, etc.)")
    parser.add_argument("-m", "--model", default="medium", choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo de Whisper (default: medium)")
    parser.add_argument("-l", "--lang", default="es",
                        help="Idioma del audio (default: es)")
    parser.add_argument("-f", "--format", default="txt", choices=["txt", "srt", "all"],
                        help="Formato de salida (default: txt)")
    parser.add_argument("-o", "--output", default=None,
                        help="Directorio de salida (default: mismo dir que el video)")
    parser.add_argument("--no-cleanup", action="store_true",
                        help="No eliminar el audio temporal (WAV)")
    args = parser.parse_args()

    video_path = args.video
    if not os.path.isfile(video_path):
        print(f"✗ No encontré: {video_path}")
        sys.exit(1)

    base_name = Path(video_path).stem
    output_dir = args.output or str(Path(video_path).parent)

    # Info
    duration = get_duration(video_path)
    mins, secs = divmod(int(duration), 60)
    print(f"Video: {video_path}")
    print(f"Duracion: {mins}:{secs:02d}")
    print(f"Modelo: {args.model} | Idioma: {args.lang} | Formato: {args.format}")
    print()

    # Extraer audio a temp
    with tempfile.TemporaryDirectory(prefix="whisper_") as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        print("1/3 Extrayendo audio...")
        extract_audio(video_path, audio_path)

        print("2/3 Transcribiendo...")
        result = transcribe(audio_path, args.model, args.lang)

    # Si --no-cleanup, re-extraemos a un archivo persistente
    if args.no_cleanup:
        persistent_audio = os.path.join(output_dir, f"{base_name}.wav")
        extract_audio(video_path, persistent_audio)

    print("3/3 Guardando...")
    saved = save_transcription(result, output_dir, base_name, args.format)

    print()
    print("Listo!")
    for path in saved:
        print(f"   {path}")


if __name__ == "__main__":
    main()
