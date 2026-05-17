#!/usr/bin/env python3
"""
ingest.py — YouTube → Audio → Transcription → Smart Summary → Obsidian

Pipeline:
  1. yt-dlp downloads audio (best quality, m4a/opus → wav)
  2. Whisper transcribes
  3. LLM generates smart summary
  4. Both files saved to Obsidian vault
  5. Temp audio cleaned up

Usage:
  python ingest.py <youtube-url> <obsidian-dest-dir>
  python ingest.py <youtube-url> <obsidian-dest-dir> --model medium --lang en
  python ingest.py <youtube-url> <obsidian-dest-dir> --no-summary
  python ingest.py <youtube-url> <obsidian-dest-dir> --keep-audio
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


# ── Step 1: Download audio ──────────────────────────────────────────────

def download_audio(url: str, output_path: str) -> dict:
    """Download audio from YouTube. Returns metadata dict."""
    # First, get metadata
    meta_cmd = [
        "yt-dlp", "--no-download", "--print-json",
        "--no-playlist", url,
    ]
    try:
        result = subprocess.run(meta_cmd, capture_output=True, text=True, check=True)
        meta = json.loads(result.stdout.strip().split('\n')[0])
    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError):
        meta = {}

    title = meta.get("title", "unknown")
    channel = meta.get("channel", meta.get("uploader", "unknown"))
    duration = meta.get("duration", 0)
    video_id = meta.get("id", "")
    description = meta.get("description", "")[:500] if meta.get("description") else ""

    print(f"  📺 {title}")
    print(f"     Channel: {channel} | Duration: {duration}s | ID: {video_id}")

    # Download audio as wav
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-x",                          # extract audio
        "--audio-format", "wav",
        "--audio-quality", "0",        # best
        "--postprocessor-args", "-ar 16000 -ac 1",  # 16kHz mono for whisper
        "-o", output_path,
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ Audio downloaded")

    return {
        "title": title,
        "channel": channel,
        "duration": duration,
        "video_id": video_id,
        "url": url,
        "description": description,
    }


# ── Step 2: Transcribe ──────────────────────────────────────────────────

def transcribe(audio_path: str, model_name: str, language: str) -> dict:
    """Transcribe audio with Whisper. Returns result dict."""
    import whisper

    print(f"  🎙 Transcribing with {model_name}...")
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, language=language, verbose=False)
    print(f"  ✓ Transcribed ({len(result.get('segments', []))} segments)")
    return result


# ── Step 3: Format transcription ────────────────────────────────────────

def format_transcription(result: dict, meta: dict) -> str:
    """Format transcription as a clean Obsidian note."""
    lines = [
        f"# {meta['title']}",
        "",
        f"**Fuente:** YouTube ({meta['video_id']})",
        f"**Canal:** {meta['channel']}",
        f"**Duración:** {meta['duration'] // 60}:{meta['duration'] % 60:02d}",
        f"**URL:** {meta['url']}",
        f"**Fecha transcripción:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Modelo:** Whisper {args.model} ({args.lang})",
        "",
        "---",
        "",
    ]

    # Add paragraphs from segments
    for seg in result.get("segments", []):
        text = seg["text"].strip()
        if text:
            lines.append(text)
            lines.append("")

    return "\n".join(lines)


def slugify(text: str) -> str:
    """Convert title to filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].strip('-')


# ── Step 4: Smart Summary (LLM) ─────────────────────────────────────────

def generate_summary(transcription: str, meta: dict) -> str:
    """Use local LLM to generate a smart summary."""
    llm_base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    llm_model = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")

    print(f"  🧠 Generating summary with {llm_model}...")

    # Truncate transcription for the prompt (keep first ~12K chars)
    text = transcription[:12000]
    if len(transcription) > 12000:
        text += "\n\n[... contenido truncado ...]"

    prompt = f"""Generá un resumen inteligente en español de esta transcripción.

Título: {meta['title']}
Canal: {meta['channel']}
URL: {meta['url']}

Estructura del resumen:
1. **Tesis central** — idea principal en 1-2 oraciones
2. **Temas clave** — cada tema con bullets concisos
3. **Quotes destacadas** — 3-5 citas textuales importantes (en idioma original)
4. **Aplicaciones prácticas** — qué se puede hacer con esta info

Reglas:
- Respondé en español
- Sé conciso y denso (no verbose)
- Cita timestamps cuando sea relevante

Transcripción:
{text}"""

    import urllib.request
    import json as _json

    payload = _json.dumps({
        "model": llm_model,
        "messages": [
            {"role": "system", "content": "Sos un experto en síntesis de contenido. Generás resúmenes densos y útiles."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{llm_base}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = _json.loads(resp.read())
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                print(f"  ✓ Summary generated ({len(content)} chars)")
                return content
    except Exception as e:
        print(f"  ⚠ Summary failed: {e}")

    return ""


def format_summary(summary: str, meta: dict) -> str:
    """Format summary as Obsidian note."""
    lines = [
        f"# {meta['title']} — Resumen",
        "",
        f"**Fuente:** YouTube ({meta['video_id']})",
        f"**Canal:** {meta['channel']}",
        f"**URL:** {meta['url']}",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        summary,
        "",
    ]

    if meta.get("description"):
        lines += [
            "---",
            "",
            "## Descripción original",
            "",
            meta["description"],
        ]

    return "\n".join(lines)


# ── Main Pipeline ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube → Transcription → Summary → Obsidian",
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("dest", help="Destination directory in Obsidian vault")
    parser.add_argument("-m", "--model", default="medium", help="Whisper model (default: medium)")
    parser.add_argument("-l", "--lang", default="en", help="Audio language (default: en)")
    parser.add_argument("--no-summary", action="store_true", help="Skip LLM summary generation")
    parser.add_argument("--keep-audio", action="store_true", help="Keep audio file")
    global args
    args = parser.parse_args()

    url = args.url
    dest = os.path.expanduser(args.dest)

    # Ensure dest exists
    os.makedirs(dest, exist_ok=True)

    print(f"🎬 Ingesting: {url}")
    print(f"   → {dest}")
    print()

    with tempfile.TemporaryDirectory(prefix="yt-ingest-") as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # Step 1: Download
        print("1/4 Downloading audio...")
        meta = download_audio(url, audio_path)

        slug = slugify(meta["title"])
        transcription_path = os.path.join(dest, f"{slug}-transcripcion.md")
        summary_path = os.path.join(dest, f"{slug}-resumen.md")

        # Keep audio if requested
        if args.keep_audio:
            import shutil
            audio_dest = os.path.join(dest, f"{slug}.wav")
            shutil.copy2(audio_path, audio_dest)
            print(f"  ✓ Audio saved to {audio_dest}")

        # Step 2: Transcribe
        print("2/4 Transcribing...")
        result = transcribe(audio_path, args.model, args.lang)

        # Step 3: Save transcription
        print("3/4 Saving transcription...")
        transcription_md = format_transcription(result, meta)
        Path(transcription_path).write_text(transcription_md, encoding="utf-8")
        print(f"  ✓ Transcription: {transcription_path}")

        # Step 4: Smart Summary
        if not args.no_summary:
            print("4/4 Generating smart summary...")
            summary_text = generate_summary(transcription_md, meta)
            if summary_text:
                summary_md = format_summary(summary_text, meta)
                Path(summary_path).write_text(summary_md, encoding="utf-8")
                print(f"  ✓ Summary: {summary_path}")
            else:
                print("  ⚠ Summary skipped (LLM unavailable)")
        else:
            print("4/4 Summary skipped (--no-summary)")

    print()
    print(f"✅ Done! Files saved to {dest}")
    if not args.no_summary:
        print(f"   📄 {slug}-transcripcion.md")
        print(f"   📄 {slug}-resumen.md")
    else:
        print(f"   📄 {slug}-transcripcion.md")


if __name__ == "__main__":
    main()
