"""Generate the synthetic demo debate with text-to-speech (session 15).

Reads demo/guion.md and writes demo/<ID>.mp3 for each speech, giving each
speaker a different voice. Usage: .venv/bin/python scripts/make_demo_debate.py
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Each speaker keeps the same voice in the constructive speech and the reply.
VOICES = {"P1": "coral", "O1": "ash", "P2": "nova", "O2": "onyx", "P3": "echo", "O3": "shimmer", "OR": "ash", "PR": "coral"}
STYLE = ("Eres un estudiante de secundaria peruano en un torneo de debate escolar. "
         "Habla en español latinoamericano, con energía y seguridad, ritmo de discurso.")


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    text = (ROOT / "demo" / "guion.md").read_text()
    for sid, body in re.findall(r"^## (\w+)\n(.+?)(?=\n## |\Z)", text, flags=re.S | re.M):
        out = ROOT / "demo" / f"{sid}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts", voice=VOICES[sid], input=body.strip(), instructions=STYLE,
        ) as r:
            r.stream_to_file(out)
        print("ok", out.name)


if __name__ == "__main__":
    main()
