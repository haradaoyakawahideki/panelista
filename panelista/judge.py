"""The AI judge: LLM with structured outputs (session 08).

segment(): splits one full recording into WSDC speeches (the upload fallback).
judge(): turns the speech transcripts into a ballot with clashes, readings
and speaker points.
"""
import os
from typing import Dict, List

from openai import OpenAI

from .schemas import Balota, Segmentacion
from .transcribe import as_text
from .wsdc import RUBRIC, SPEECHES, SPEECH_IDS

MODEL = os.getenv("PANELISTA_MODEL", "gpt-4.1")

SYSTEM = f"""Eres un juez experimentado de debate escolar en el Perú que
ayuda a docentes que recién aprenden a juzgar. Juzgas solo con lo que dice
la transcripción: no inventes argumentos ni citas. Cada afirmación sobre un
orador debe apoyarse en una cita textual corta con su minuto. Si la
transcripción no alcanza para juzgar algo (por ejemplo, el lenguaje corporal),
dilo en las advertencias. Escribe en español claro, para un docente.

{RUBRIC}

Reglas de salida:
- Identifica de 2 a 4 choques, ordenados por peso.
- Un puntaje por discurso, con estilo + contenido + estrategia = total y
  dentro de los rangos del formato.
- La suma de puntos del ganador debe ser mayor que la del perdedor.
- La lectura alternativa es la mejor defensa honesta del otro resultado.
"""


def segment(client: OpenAI, segments: List[dict]) -> Dict[str, List[dict]]:
    """Find where each speech starts in a single full-debate recording."""
    numbered = "\n".join(f"{i}: [{s['start']:.0f}s] {s['text']}" for i, s in enumerate(segments))
    order = ", ".join(f"{s['id']} ({s['rol']})" for s in SPEECHES)
    r = client.responses.parse(
        model=MODEL,
        instructions=(
            "Divide la transcripción de un debate WSDC en sus discursos. El orden es "
            f"fijo: {order}. Busca cambios de orador: saludos ('Señora presidenta…'), "
            "cierres ('Gracias'), anuncios del moderador y pausas largas. Devuelve el "
            "índice del primer segmento de cada discurso, en orden creciente."
        ),
        input=numbered,
        text_format=Segmentacion,
    )
    starts = {c.discurso: c.inicio_segmento for c in r.output_parsed.cortes}
    idx = [starts.get(sid, 0) for sid in SPEECH_IDS] + [len(segments)]
    out = {}
    for k, sid in enumerate(SPEECH_IDS):
        out[sid] = segments[idx[k]: max(idx[k], idx[k + 1])]
    return out


def judge(client: OpenAI, motion: str, names: Dict[str, str], speeches: Dict[str, List[dict]]) -> Balota:
    blocks = []
    for s in SPEECHES:
        segs = speeches.get(s["id"]) or []
        if segs:  # make times relative to the start of each speech
            t0 = segs[0]["start"]
            segs = [{**x, "start": x["start"] - t0} for x in segs]
        body = as_text(segs) if segs else "(sin audio)"
        blocks.append(f"### {s['id']} · {s['rol']} · {names.get(s['id'], '')}\n{body}")
    prompt = f"Moción: {motion}\n\n" + "\n\n".join(blocks)
    r = client.responses.parse(model=MODEL, instructions=SYSTEM, input=prompt, text_format=Balota)
    return r.output_parsed
