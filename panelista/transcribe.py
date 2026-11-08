"""Speech to text with Whisper (session 13).

Phone recordings get compressed to 16 kHz mono MP3, cut into 5-minute pieces
and transcribed in parallel (an 80-minute debate takes about 2 minutes instead
of 24). Each segment keeps its timestamps. Repeated lines, which Whisper invents
during music or silence, are dropped.
"""
import subprocess
from concurrent.futures import ThreadPoolExecutor
import tempfile
from pathlib import Path
from typing import List

from openai import OpenAI

CHUNK_SECONDS = 5 * 60
WORKERS = 8
MODEL = "whisper-1"  # the model that returns timestamped segments
PROMPT = (
    "Debate escolar en formato WSDC. Señora presidenta, honorables jueces, "
    "Proposición, Oposición, moción, réplica, punto de información."
)


def _compress(src: Path, dst: Path) -> Path:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
           "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", str(dst)]
    subprocess.run(cmd, check=True)
    return dst


def _split(src: Path, folder: Path) -> List[Path]:
    """Cut into CHUNK_SECONDS pieces (part000.mp3, part001.mp3, ...)."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-f", "segment",
                    "-segment_time", str(CHUNK_SECONDS), "-c", "copy", str(folder / "part%03d.mp3")],
                   check=True)
    return sorted(folder.glob("part*.mp3"))


def _one(client: OpenAI, offset: float, piece: Path) -> List[dict]:
    with open(piece, "rb") as f:
        r = client.audio.transcriptions.create(
            model=MODEL, file=f, language="es", prompt=PROMPT,
            response_format="verbose_json", timestamp_granularities=["segment"],
        )
    return [{"start": x.start + offset, "end": x.end + offset, "text": x.text.strip()}
            for x in (r.segments or []) if getattr(x, "no_speech_prob", 0) < 0.8]


def transcribe(client: OpenAI, audio: Path) -> List[dict]:
    """Return [{start, end, text}] with times in seconds from the start of the file."""
    tmp = Path(tempfile.mkdtemp())
    small = _compress(Path(audio), tmp / "full.mp3")
    pieces = [(i * CHUNK_SECONDS, p) for i, p in enumerate(_split(small, tmp))]
    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(lambda a: _one(client, *a), pieces))
    segments, last = [], None
    for seg in (x for part in parts for x in part):
        if seg["text"] and seg["text"] != last:  # drop repeated lines
            segments.append(seg)
        last = seg["text"]
    return segments

def mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def as_text(segments: List[dict]) -> str:
    return "\n".join(f"[{mmss(s['start'])}] {s['text']}" for s in segments)
