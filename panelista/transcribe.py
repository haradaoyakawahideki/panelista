"""Speech to text with Whisper (session 13).

Phone recordings get compressed to 16 kHz mono MP3. Anything still over the
API's 25 MB limit gets split into 20-minute pieces. Each segment keeps its
timestamps.
"""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List

from openai import OpenAI

MAX_BYTES = 24 * 1024 * 1024
CHUNK_SECONDS = 20 * 60
MODEL = "whisper-1"  # the model that returns timestamped segments
PROMPT = (
    "Debate escolar en formato WSDC. Señora presidenta, honorables jueces, "
    "Proposición, Oposición, moción, réplica, punto de información."
)


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def _compress(src: Path, dst: Path, start: float = 0, length: float = None) -> Path:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-i", str(src)]
    if length:
        cmd += ["-t", str(length)]
    cmd += ["-ac", "1", "-ar", "16000", "-b:a", "32k", str(dst)]
    subprocess.run(cmd, check=True)
    return dst


def transcribe(client: OpenAI, audio: Path) -> List[dict]:
    """Return [{start, end, text}] with times in seconds from the start of the file."""
    audio = Path(audio)
    tmp = Path(tempfile.mkdtemp())
    small = _compress(audio, tmp / "full.mp3")
    pieces = [(0.0, small)]
    if small.stat().st_size > MAX_BYTES:
        total = duration(small)
        pieces = [
            (t, _compress(audio, tmp / f"part{i}.mp3", t, CHUNK_SECONDS))
            for i, t in enumerate(range(0, int(total) + 1, CHUNK_SECONDS))
        ]
    segments = []
    for offset, piece in pieces:
        with open(piece, "rb") as f:
            r = client.audio.transcriptions.create(
                model=MODEL, file=f, language="es", prompt=PROMPT,
                response_format="verbose_json", timestamp_granularities=["segment"],
            )
        for s in r.segments or []:
            segments.append({"start": s.start + offset, "end": s.end + offset, "text": s.text.strip()})
    return segments


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def as_text(segments: List[dict]) -> str:
    return "\n".join(f"[{mmss(s['start'])}] {s['text']}" for s in segments)
