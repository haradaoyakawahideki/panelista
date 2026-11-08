# Comparación de modelos para juzgar (7 nov 2026)

**Prueba:** el debate de demostración sintético (`demo/guion.md`): 8 discursos, 5,8 minutos de audio.
Todos los modelos reciben la misma transcripción y las mismas reglas (`panelista/wsdc.py`), y cada uno corre **3 veces**.
El script es `scripts/compare_models.py`.

**Cómo se mide la precisión.** El guion se escribió con respuestas correctas conocidas. Se revisan seis cosas:
1. Da puntaje a los 8 discursos.
2. Gana Oposición.
3. P2 es el discurso más débil de Proposición.
4. O3 recibe menos puntos que O2 por traer un argumento nuevo.
5. Los puntajes se dispersan (4 puntos o más entre los discursos constructivos).
6. Todas las citas existen de verdad en la transcripción.

| Modelo | Aciertos (3 corridas) | Tiempo del juicio | USD por juicio (demo) | Citas inventadas |
|---|---|---|---|---|
| gpt-4.1 | 15/18 | ~21 s | $0.038 | 2 de 52 |
| gpt-5.5 | 17/18 | ~71 s | $0.187 | 0 |
| gpt-5.6-sol | **18/18** | ~61 s | $0.149 | 0 |
| gpt-5.6-luna | **18/18** | ~49 s | **$0.008** | 0 |

**Otra observación.** En una corrida exploratoria previa, gpt-5.5 devolvió puntaje para 1 solo de los 8 discursos.
En esa misma corrida, gpt-4.1 puso a P2 por encima de P1.

## Costo estimado para un debate real (unos 60 minutos)

Para un debate de 60 minutos, la transcripción es unas 10 veces más larga que la del demo.

| | Whisper | Juicio | Total por debate | 4 debates al mes por colegio |
|---|---|---|---|---|
| gpt-5.6-luna | $0.36 | ~$0.02 | **~$0.38** | ~$1.50 |
| gpt-4.1 | $0.36 | ~$0.12 | ~$0.48 | ~$1.90 |
| gpt-5.6-sol | $0.36 | ~$0.30 | ~$0.66 | ~$2.60 |
| gpt-5.5 | $0.36 | ~$0.40 | ~$0.76 | ~$3.00 |

Precios: página de precios de OpenAI, 7 nov 2026. El precio de gpt-5.6-sol es promocional hasta el 30 nov 2026.

## Límites de esta prueba

- Un solo debate, sintético, y las "respuestas correctas" las definió el autor del guion. No es un juez humano.
- Todos los modelos comprimen los puntajes cerca de 70, más de lo que lo haría un juez experimentado.
- El siguiente paso es comparar con resultados reales del MED y con las correcciones de jueces humanos en la beta.
