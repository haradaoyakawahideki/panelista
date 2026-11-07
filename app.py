"""Panelista: an AI judging assistant for school debate in WSDC format (beta)."""
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from openai import OpenAI

from panelista import store
from panelista.judge import MODEL, judge, segment
from panelista.transcribe import as_text, transcribe
from panelista.wsdc import SPEECHES, SPEECH_IDS

ROOT = Path(__file__).parent
DEMO = ROOT / "demo"

st.set_page_config(page_title="Panelista", page_icon="⚖️", layout="centered")


def get_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            key = None
    if not key:
        st.error("Falta OPENAI_API_KEY (en .env o en los secrets de Streamlit).")
        st.stop()
    return OpenAI(api_key=key)


try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

ss = st.session_state
ss.setdefault("audios", {})       # speech id -> bytes
ss.setdefault("transcripts", {})  # audio hash -> segments
ss.setdefault("result", None)

# ---------- header ----------
st.title("⚖️ Panelista")
st.caption("Tu co-juez de debate escolar WSDC · **versión beta**")
with st.expander("Antes de empezar: qué hace y qué no hace (beta)"):
    st.markdown(
        "- Escucha el debate, encuentra los **choques**, propone **lecturas** y sugiere **puntajes de orador**.\n"
        "- Juzga **solo lo que se oye**: no ve el lenguaje corporal ni los materiales.\n"
        "- Es una **sugerencia para el docente**, no una decisión final. Aún estamos midiendo su precisión frente a jueces humanos.\n"
        "- Al subir el audio, el colegio confirma que tiene el **consentimiento de los padres** de los oradores."
    )

with st.sidebar:
    st.header("Colegio")
    school = st.text_input("Código del colegio", value="demo-lpde")
    left = store.remaining(school)
    st.metric("Debates disponibles este mes", f"{left} / {store.LIMIT}")
    st.divider()
    if st.button("Cargar debate de demostración", use_container_width=True):
        names = {}
        for line in (DEMO / "oradores.txt").read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                names[k.strip()] = v.strip()
        ss["motion"] = names.pop("MOCION", "")
        for sid in SPEECH_IDS:
            ss[f"name_{sid}"] = names.get(sid, "")
            ss["audios"][sid] = (DEMO / f"{sid}.mp3").read_bytes()
        ss["mode"] = "Grabar o subir cada discurso"
        ss["result"] = None
        st.rerun()
    st.caption(f"Modelo: {MODEL} · Transcripción: Whisper")

# ---------- 1. ballot ----------
st.subheader("1 · Balota")
motion = st.text_input("Moción", key="motion", placeholder="Esta Cámara…")
c1, c2 = st.columns(2)
names = {}
for s in SPEECHES:
    col = c1 if s["bando"] == "Proposición" else c2
    names[s["id"]] = col.text_input(f"{s['id']} · {s['rol']}", key=f"name_{s['id']}")

# ---------- 2. audio ----------
st.subheader("2 · Audio")
mode = st.radio(
    "¿Cómo envías el debate?",
    ["Grabar o subir cada discurso", "Subir la grabación completa"],
    key="mode", horizontal=True,
)
full_audio = None
if mode == "Grabar o subir cada discurso":
    st.caption("En orden: toca grabar cuando empieza cada orador y detén al terminar.")
    for s in SPEECHES:
        sid = s["id"]
        with st.container(border=True):
            st.markdown(f"**{sid} · {s['rol']}** — {names.get(sid) or '…'}")
            if sid in ss["audios"]:
                st.audio(ss["audios"][sid])
                if st.button("Borrar y volver a grabar", key=f"del_{sid}"):
                    del ss["audios"][sid]
                    st.rerun()
            else:
                rec = st.audio_input("Grabar", key=f"rec_{sid}", label_visibility="collapsed")
                up = st.file_uploader("…o subir archivo", type=["mp3", "m4a", "wav", "ogg", "webm", "aac"], key=f"up_{sid}")
                if rec or up:
                    ss["audios"][sid] = (rec or up).getvalue()
                    st.rerun()
else:
    up = st.file_uploader("Grabación completa del debate", type=["mp3", "m4a", "wav", "ogg", "webm", "aac", "mp4"])
    if up:
        full_audio = up.getvalue()
        st.audio(full_audio)
    st.caption("Panelista detecta dónde empieza cada discurso. Revisa el corte en el resultado.")


def transcribe_bytes(client, data: bytes):
    h = hashlib.sha1(data).hexdigest()
    if h not in ss["transcripts"]:
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as f:
            f.write(data)
        ss["transcripts"][h] = transcribe(client, Path(f.name))
    return ss["transcripts"][h]


# ---------- 3. judge ----------
st.subheader("3 · Juzgar")
ready = bool(full_audio) or len(ss["audios"]) == len(SPEECH_IDS)
if not ready and mode == "Grabar o subir cada discurso":
    st.info(f"Faltan {len(SPEECH_IDS) - len(ss['audios'])} discursos.")
if st.button("Juzgar el debate", type="primary", disabled=not ready or left <= 0, use_container_width=True):
    client = get_client()
    with st.status("Panelista está juzgando…", expanded=True) as status:
        if full_audio:
            st.write("Transcribiendo la grabación completa…")
            segs = transcribe_bytes(client, full_audio)
            st.write("Encontrando dónde empieza cada discurso…")
            speeches = segment(client, segs)
        else:
            speeches = {}
            for s in SPEECHES:
                st.write(f"Transcribiendo {s['id']} · {names.get(s['id']) or s['rol']}…")
                speeches[s["id"]] = transcribe_bytes(client, ss["audios"][s["id"]])
        st.write("Identificando choques y puntajes…")
        ballot = judge(client, motion, names, speeches)
        store.register_use(school)
        ss["result"] = {"ballot": ballot, "speeches": speeches, "names": dict(names), "motion": motion}
        status.update(label="Listo", state="complete")

# ---------- results ----------
res = ss["result"]
if res:
    b = res["ballot"]
    by_id = {p.discurso: p for p in b.puntajes}
    tot = {"Proposición": 0, "Oposición": 0}
    for s in SPEECHES:
        if s["id"] in by_id:
            tot[s["bando"]] += by_id[s["id"]].total
    st.success(f"**Gana {b.ganador}** · Proposición {tot['Proposición']} – Oposición {tot['Oposición']} · confianza {b.confianza}")
    st.write(b.resumen)

    st.markdown("#### Choques")
    for ch in b.choques:
        with st.expander(f"{'🔴' if ch.peso == 'alto' else '🟠' if ch.peso == 'medio' else '⚪'} {ch.titulo} → {ch.ganador}"):
            st.markdown(f"**Proposición:** {ch.proposicion}\n\n**Oposición:** {ch.oposicion}\n\n**Por qué gana {ch.ganador}:** {ch.por_que}")
            for c in ch.citas:
                st.caption(f"{c.discurso} · {c.minuto} — “{c.texto}”")

    st.markdown("#### Lecturas posibles")
    st.markdown(f"**Principal (gana {b.lectura_principal.ganador}):** {b.lectura_principal.argumento}")
    st.markdown(f"**Alternativa (gana {b.lectura_alternativa.ganador}):** {b.lectura_alternativa.argumento}")

    st.markdown("#### Puntajes de orador sugeridos")
    st.dataframe(
        [{"Discurso": s["id"], "Orador": res["names"].get(s["id"], ""), "Estilo": by_id[s["id"]].estilo,
          "Contenido": by_id[s["id"]].contenido, "Estrategia": by_id[s["id"]].estrategia, "Total": by_id[s["id"]].total}
         for s in SPEECHES if s["id"] in by_id],
        hide_index=True, use_container_width=True,
    )
    for s in SPEECHES:
        p = by_id.get(s["id"])
        if p:
            with st.expander(f"Comentarios para {s['id']} · {res['names'].get(s['id']) or s['rol']}"):
                st.markdown(f"**Fortalezas:** {p.fortalezas}\n\n**Para mejorar:** {p.a_mejorar}")
                for c in p.citas:
                    st.caption(f"{c.minuto} — “{c.texto}”")

    if b.advertencias:
        st.warning("**Advertencias:**\n\n" + "\n".join(f"- {a}" for a in b.advertencias))

    with st.expander("Ver transcripciones"):
        for s in SPEECHES:
            st.markdown(f"**{s['id']} · {s['rol']}**")
            st.text(as_text(res["speeches"].get(s["id"], [])) or "(vacío)")

    # ---------- 4. human correction ----------
    st.subheader("4 · Tu decisión (juez humano)")
    st.caption("Tu corrección mide la precisión de Panelista y lo ayuda a mejorar.")
    with st.form("correccion"):
        h_winner = st.radio("Ganador según tú", ["Proposición", "Oposición"], horizontal=True,
                            index=0 if b.ganador == "Proposición" else 1)
        cols = st.columns(4)
        human = {}
        for i, s in enumerate(SPEECHES):
            ai = by_id[s["id"]].total if s["id"] in by_id else 70
            lo, hi = (30, 40) if s["tipo"] == "réplica" else (60, 80)
            human[s["id"]] = cols[i % 4].number_input(s["id"], lo, hi, int(min(max(ai, lo), hi)), key=f"h_{s['id']}")
        notes = st.text_area("Comentarios (opcional)")
        if st.form_submit_button("Guardar mi decisión"):
            diffs = [abs(human[k] - by_id[k].total) for k in human if k in by_id]
            mae = sum(diffs) / len(diffs) if diffs else 0
            store.save_correction({
                "fecha": datetime.now().isoformat(timespec="seconds"), "colegio": school,
                "mocion": res["motion"], "modelo": MODEL,
                "ia": {"ganador": b.ganador, "puntajes": {k: v.total for k, v in by_id.items()}},
                "humano": {"ganador": h_winner, "puntajes": human, "notas": notes},
            })
            st.success(f"Guardado. Coincidencia en el ganador: {'sí' if h_winner == b.ganador else 'no'} · "
                       f"diferencia promedio de puntaje: {mae:.1f} puntos.")
