"""Compare judging models on the synthetic demo debate: accuracy, time and price.

The demo script was written with known 'right answers', which we check
automatically:
  1. Oposición wins (Proposición never answers the Chile evidence).
  2. P2 is the weakest Proposición constructive (almost no rebuttal).
  3. O3 gets less than O2 for bringing a new argument (vote buying).
  0. All 8 speeches get points.
  4. Speaker points spread out (range of constructives >= 4).
  5. Quotes exist in the transcript (no invented quotes).
Usage: .venv/bin/python scripts/compare_models.py gpt-4.1 gpt-5.5 ...
"""
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from panelista import judge as J  # noqa: E402
from panelista.schemas import Balota  # noqa: E402
from panelista.transcribe import as_text, transcribe  # noqa: E402
from panelista.wsdc import SPEECHES, SPEECH_IDS  # noqa: E402

# USD per 1M tokens (input, output), standard tier, from the OpenAI pricing page on 2026-11-07
PRICES = {"gpt-4.1": (2.00, 8.00), "gpt-4.1-mini": (0.40, 1.60), "gpt-5.5": (5.00, 30.00),
          "gpt-5.4": (2.50, 15.00), "gpt-5.4-mini": (0.75, 4.50), "gpt-5.6-luna": (0.20, 1.20),
          "gpt-5.6-sol": (4.00, 20.00), "gpt-5.6-terra": (2.00, 12.00)}
WHISPER_PER_MIN = 0.006
OUT = ROOT / "docs" / "evaluacion"
RUNS = 3


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if not unicodedata.combining(c)))


def load_transcripts(client):
    cache = OUT / "demo_transcripts.json"
    if cache.exists():
        return json.loads(cache.read_text())
    sp = {sid: transcribe(client, ROOT / "demo" / f"{sid}.mp3") for sid in SPEECH_IDS}
    cache.write_text(json.dumps(sp, ensure_ascii=False, indent=1))
    return sp


def run(client, model, motion, names, sp):
    blocks = []
    for s in SPEECHES:
        segs = sp[s["id"]]
        t0 = segs[0]["start"]
        segs = [{**x, "start": x["start"] - t0} for x in segs]
        blocks.append(f"### {s['id']} · {s['rol']} · {names.get(s['id'], '')}\n{as_text(segs)}")
    t = time.time()
    r = client.responses.parse(model=model, instructions=J.SYSTEM,
                               input=f"Moción: {motion}\n\n" + "\n\n".join(blocks), text_format=Balota)
    secs = time.time() - t
    u = r.usage
    pin, pout = PRICES[model]
    cost = u.input_tokens / 1e6 * pin + u.output_tokens / 1e6 * pout
    return r.output_parsed, secs, u.input_tokens, u.output_tokens, cost


def checks(b, sp):
    pts = {p.discurso: p.total for p in b.puntajes}
    full = norm(" ".join(x["text"] for v in sp.values() for x in v))
    quotes = [c.texto for ch in b.choques for c in ch.citas] + [c.texto for p in b.puntajes for c in p.citas]
    real = sum(1 for q in quotes if norm(q)[:40] in full)
    cons = [pts[i] for i in ("P1", "O1", "P2", "O2", "P3", "O3") if i in pts]
    return {
        "ocho_puntajes": all(i in pts for i in SPEECH_IDS),
        "gana_oposicion": b.ganador == "Oposición",
        "p2_mas_bajo_de_prop": pts.get("P2", 99) < min(pts.get("P1", 0), pts.get("P3", 0)),
        "o3_menor_que_o2": pts.get("O3", 99) < pts.get("O2", 0),
        "puntajes_dispersos": len(cons) == 6 and max(cons) - min(cons) >= 4,
        "citas_reales": f"{real}/{len(quotes)}",
        "_citas_ok": len(quotes) > 0 and real == len(quotes),
        "puntajes": pts,
    }


def main(models):
    client = OpenAI()
    names = dict(l.split(":", 1) for l in (ROOT / "demo" / "oradores.txt").read_text().splitlines())
    names = {k.strip(): v.strip() for k, v in names.items()}
    motion = names.pop("MOCION")
    OUT.mkdir(parents=True, exist_ok=True)
    sp = load_transcripts(client)
    minutes = sum(v[-1]["end"] for v in sp.values()) / 60
    rows = []
    for m in [m for m in models for _ in range(RUNS)]:
        try:
            b, secs, tin, tout, cost = run(client, m, motion, names, sp)
        except Exception as e:  # keep going if one model fails
            print(m, "ERROR", e)
            continue
        c = checks(b, sp)
        score = sum(c[k] for k in ("ocho_puntajes", "gana_oposicion", "p2_mas_bajo_de_prop", "o3_menor_que_o2",
                                   "puntajes_dispersos", "_citas_ok"))
        rows.append({"modelo": m, "aciertos": f"{score}/6", "segundos": round(secs, 1),
                     "tokens_in": tin, "tokens_out": tout, "usd_juicio": round(cost, 4), **c})
        (OUT / f"balota_{m}_{len(rows)}.json").write_text(b.model_dump_json(indent=1))
        print(json.dumps(rows[-1], ensure_ascii=False))
    (OUT / "comparacion_modelos.json").write_text(json.dumps(
        {"audio_minutos": round(minutes, 2), "usd_whisper": round(minutes * WHISPER_PER_MIN, 4), "resultados": rows},
        ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or ["gpt-4.1", "gpt-5.5", "gpt-5.6-sol", "gpt-5.6-luna"])
