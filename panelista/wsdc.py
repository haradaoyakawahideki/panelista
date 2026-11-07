"""WSDC format rules: the fixed speech order and the scoring rubric."""

# WSDC speech order: 3 constructive speeches per side, alternating, then
# the replies (opposition first). Each reply is given by the 1st or 2nd speaker.
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
Formato WSDC (World Schools Debating Championships).

Puntaje de cada discurso constructivo: 60 a 80 puntos.
  - Estilo 40 % (24-32): claridad, ritmo, contacto, uso del lenguaje.
  - Contenido 40 % (24-32): calidad de los argumentos y de la evidencia,
    análisis, refutación; se juzga como si lo leyera un lector razonable.
  - Estrategia 20 % (12-16): estructura, manejo del tiempo, comprensión del
    rol, identificación de los choques importantes, respuesta a los POIs.
Puntaje de réplica: 30 a 40 puntos (la mitad de la escala): Estilo 12-16,
Contenido 12-16, Estrategia 6-8.

Escala orientativa de un discurso constructivo:
  60-63 débil, 64-67 por debajo del promedio, 68-72 promedio (70 = promedio
  de un torneo escolar), 73-76 muy bueno, 77-80 excepcional.

Roles:
  - 1.er orador: define la moción, presenta el modelo o la postura y el
    reparto de argumentos del equipo. El 1.º de Oposición además refuta.
  - 2.º orador: refuta y desarrolla argumentos nuevos de su equipo.
  - 3.er orador: refuta y reconstruye; organiza el debate en choques.
    No debe introducir argumentos nuevos importantes.
  - Réplica: resumen sesgado del debate, choque por choque, explicando por
    qué ganó su equipo. No puede traer argumentos nuevos.

Cómo se decide: el juez decide qué equipo fue más persuasivo en conjunto,
evaluando los choques centrales del debate y cuánto pesa cada uno. El
equipo ganador debe tener la suma de puntos más alta (no hay empates).
""".strip()
