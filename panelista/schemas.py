"""Pydantic schemas that force the model to return a structured ballot."""
from typing import List, Literal

from pydantic import BaseModel, Field

Bando = Literal["Proposición", "Oposición"]


class Cita(BaseModel):
    discurso: str = Field(description="Id del discurso: P1, O1, P2, O2, P3, O3, OR o PR")
    minuto: str = Field(description="Minuto aproximado dentro del discurso, formato m:ss")
    texto: str = Field(description="Cita textual corta tomada de la transcripción")


class Choque(BaseModel):
    titulo: str = Field(description="Pregunta central del choque, en una línea")
    proposicion: str = Field(description="Qué sostuvo Proposición en este choque")
    oposicion: str = Field(description="Qué sostuvo Oposición en este choque")
    tipo: Literal["explícito", "caracterización", "criterio", "implícito"]
    ganador: Bando
    por_que: str = Field(description="Por qué ese bando ganó el choque: respuestas, reconstrucción, solidez")
    margen: Literal["claro", "estrecho"] = Field(description="Claro = refutación contundente; estrecho = por matiz")
    peso: Literal["alto", "medio", "bajo"]
    por_que_peso: str = Field(description="Por qué pesa eso: centralidad, magnitud, ponderación de los equipos")
    citas: List[Cita]


class PuntajeOrador(BaseModel):
    discurso: str = Field(description="Id del discurso")
    estilo: int
    contenido: int
    estrategia: int
    total: int
    fortalezas: str
    a_mejorar: str = Field(description="El principal aspecto a mejorar, según su rol")
    como_corregir: str = Field(description="Cómo pudo hacerlo, señalando el momento concreto del discurso")
    citas: List[Cita]


class FeedbackEquipo(BaseModel):
    bando: Bando
    que_funciono: str
    que_mejorar: str = Field(description="Espacio de mejora concreto, también si ganó")
    como: str = Field(description="Cómo mejorarlo en la próxima ronda, en tono formativo")


class Lectura(BaseModel):
    ganador: Bando
    argumento: str = Field(description="Cómo un juez razonable llegaría a este resultado")


class Balota(BaseModel):
    resumen: str = Field(description="El debate en dos o tres oraciones")
    choques: List[Choque]
    puntajes: List[PuntajeOrador]
    feedback_equipos: List[FeedbackEquipo] = Field(description="Uno para Proposición y uno para Oposición")
    ganador: Bando
    ponderacion_final: str = Field(description="Cómo se combinan los choques para decidir, y por qué")
    lectura_principal: Lectura
    lectura_alternativa: Lectura = Field(
        description="La mejor lectura posible a favor del otro resultado o de un camino distinto"
    )
    confianza: Literal["alta", "media", "baja"]
    advertencias: List[str] = Field(
        description="Limitaciones: audio poco claro, discursos cortados, cosas que no se pueden juzgar solo con audio"
    )


class Corte(BaseModel):
    discurso: str
    inicio_segmento: int = Field(description="Índice del segmento de la transcripción donde empieza el discurso")


class Segmentacion(BaseModel):
    cortes: List[Corte]
