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
    ganador: Bando
    por_que: str = Field(description="Por qué ese bando ganó el choque")
    peso: Literal["alto", "medio", "bajo"]
    citas: List[Cita]


class PuntajeOrador(BaseModel):
    discurso: str = Field(description="Id del discurso")
    estilo: int
    contenido: int
    estrategia: int
    total: int
    fortalezas: str
    a_mejorar: str = Field(description="Un consejo concreto para el orador")
    citas: List[Cita]


class Lectura(BaseModel):
    ganador: Bando
    argumento: str = Field(description="Cómo un juez razonable llegaría a este resultado")


class Balota(BaseModel):
    resumen: str = Field(description="El debate en dos o tres oraciones")
    choques: List[Choque]
    puntajes: List[PuntajeOrador]
    ganador: Bando
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
