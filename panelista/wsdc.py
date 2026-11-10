"""WSDC format rules: the fixed speech order and the judging criteria.

Sources (summarized and paraphrased, never copied in full):
- LPDE, "Manual de iniciación al debate en el formato WSDC" (2020): roles,
  speaker-point table and judging rules.
- MED Chile 2025, "Taller de Jueceo" (YouTube, w66nAWBVHss): judging by
  clashes, how to weigh them and pedagogical feedback for school students.
"""

# WSDC speech order: 3 constructive speeches per side (8 min), alternating, then
# the replies (4 min, opposition first), given by the 1st or 2nd speaker.
SPEECHES = [
    {"id": "P1", "rol": "1.er orador de Proposición", "bando": "Proposición", "tipo": "constructivo"},
    {"id": "O1", "rol": "1.er orador de Oposición", "bando": "Oposición", "tipo": "constructivo"},
    {"id": "P2", "rol": "2.º orador de Proposición", "bando": "Proposición", "tipo": "constructivo"},
    {"id": "O2", "rol": "2.º orador de Oposición", "bando": "Oposición", "tipo": "constructivo"},
    {"id": "P3", "rol": "3.er orador de Proposición", "bando": "Proposición", "tipo": "constructivo"},
    {"id": "O3", "rol": "3.er orador de Oposición", "bando": "Oposición", "tipo": "constructivo"},
    {"id": "OR", "rol": "Réplica de Oposición", "bando": "Oposición", "tipo": "réplica"},
    {"id": "PR", "rol": "Réplica de Proposición", "bando": "Proposición", "tipo": "réplica"},
]
SPEECH_IDS = [s["id"] for s in SPEECHES]

RUBRIC = """
FORMATO WSDC (según el manual de la Liga Peruana de Debate Escolar)
- Contenido: fuerza de la argumentación, incluida la calidad de la refutación.
- Estilo: capacidad de explicar de forma persuasiva (voz, retórica). Con solo
  audio NO puedes evaluar gestos ni contacto visual: dilo en las advertencias.
- Estrategia: estructura, manejo del tiempo, prioridades, comprensión de los
  temas clave, cumplimiento del rol y trabajo en equipo.
Roles:
- 1.º Proposición: define, anuncia la carga de la prueba, caracteriza a los
  actores, presenta el caso y el reparto, y desarrolla al menos un argumento.
- 1.º Oposición: puede impugnar la definición (solo aquí), presenta su caso,
  refuta a P1 y desarrolla al menos un argumento.
- 2.os oradores: refutan, reconstruyen y traen argumentos nuevos.
- 3.os oradores: refutan, reconstruyen y resumen. No traen material nuevo
  importante.
- Réplicas (1.º o 2.º orador, primero Oposición): explican los puntos de choque
  y por qué gana su casa. Sin argumentos nuevos.

TABLA DE PUNTAJES (discursos principales, /100; en la práctica 60-80)
  80 excepcional (C32 E32 Es16) · 76-79 excelente (31/31/15-16) ·
  74-75 extremadamente bueno (30/30/15) · 71-73 muy bueno (29/29/14-15) ·
  70 bueno (28/28/14) · 67-69 satisfactorio (27/27/13-14) ·
  65-66 competente (26/26/13) · 61-64 aceptable (25/25/12-13) ·
  60 mejora necesaria (24/24/12)
RÉPLICAS (/50; en la práctica 30-40): 40 excelente (16/16/8) ·
  36-39 muy bueno a excelente (15/15/7-8) · 35 bueno (14/14/7) ·
  31-34 aceptable a satisfactorio (13/13/6-7) · 30 mejora necesaria (12/12/6)
Usa números enteros. Un torneo escolar promedio ronda los 70.

CÓMO DECIDIR (taller de jueceo del MED Chile 2025)
1. Juzga por puntos de choque y cargas de la prueba, NO discurso por discurso:
   juzgar por discursos sobrepremia a los últimos o a los que suenan mejor y
   olvida las réplicas, los segundos oradores y la refutación.
2. No cuentes argumentos: importa lo que queda en pie después de la interacción.
3. Tipos de choque: explícito (A contra no-A), de caracterización (el mismo
   fenómeno descrito distinto), de criterio (marcos distintos, p. ej. bienestar
   contra derechos) e implícito (no se nombra, pero se construye en el material).
4. Resuelve cada choque: (a) la contribución inicial de cada lado en una frase;
   (b) plausibilidad y contexto para una votante promedio informada;
   (c) respuestas directas y específicas; (d) reconstrucción o
   contrarrefutación; (e) qué material es más sólido y resistió mejor.
5. Una refutación gana crédito solo si se involucra con la lógica del
   argumento, lo vuelve menos persuasivo y es plausible Y explicada. "Eso no es
   verdad" sin explicación no gana.
6. Pondera los choques por: centralidad para la moción; profundidad y magnitud
   del impacto (cuántos, cuánto, con qué certeza); fuerza narrativa acumulativa
   (si los choques ganados forman un mundo coherente); y margen de victoria
   (por refutación contundente o por matiz). Los ejemplos sustentan, pero no
   ganan choques.
7. Para ponderar usa, en orden: la ponderación explícita de los equipos, luego
   la implícita, y solo si no hay ninguna, una inferencia razonable tuya. Explica
   siempre por qué.
8. Usa los terceros discursos y las réplicas para ver qué consideran
   importante los equipos.

REGLAS DEL JUEZ (manual LPDE)
- Juzga como una persona razonable promedio, con conocimiento general y algo
  informada de la actualidad. No uses conocimiento especializado.
- Juzga el debate que ocurrió, no el que querías. No completes argumentos por
  los equipos aunque te parezcan intuitivos. No descartes argumentos porque no
  te gusten.
- Juzga equipos, no individuos. No hay "perdedores automáticos": nada aislado
  decide el debate.
- El material nuevo en un 3.er discurso o en una réplica no recibe crédito:
  dilo y explica por qué.

FEEDBACK PEDAGÓGICO (escolares)
- Muestra espacio de mejora para el equipo que gana Y para el que pierde. El
  error se puede corregir: evita que el equipo que pierde se sienta culpable.
- Explica por qué algo se ponderó o se descartó, no solo que se hizo.
- Para cada error, explica cómo se pudo corregir y señala el momento concreto
  del discurso.
- Adapta el consejo al rol: 1.os oradores en encuadre y caracterización;
  2.os en extensión y refutación; 3.os en comparativas y refutación; réplicas
  en el resumen choque por choque.
""".strip()


# Speech timing (seconds): bells as (time, strikes) and a hard recording limit.
# Constructive 8 min: 1 bell at 1:00 and 7:00 (protected time), 2 at 8:00, 3 at 8:15.
TIMING = {
    "constructivo": {"bells": [(60, 1), (420, 1), (480, 2), (495, 3)], "limit": 500},
    # Replies are 4 min with no POIs (LPDE manual), so no protected-time bells.
    "réplica": {"bells": [(240, 2), (255, 3)], "limit": 260},
}
