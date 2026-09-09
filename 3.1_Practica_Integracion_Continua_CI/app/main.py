"""
API REST del Sistema de Gestión Escolar y Becas
UAdeC — Facultad de Sistemas · Desarrollo de Proyectos de Software
"""

import os
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.school_service import (
    validar_matricula,
    calcular_promedio,
    determinar_estatus_beca,
    calcular_cuota_final,
    consultar_auditoria_academica,
)

app = FastAPI(
    title="Sistema de Gestión Escolar - API de Becas y Calificaciones",
    description=(
        "Microservicio de ejemplo para la Unidad 3.1: "
        "Integración Continua (CI) con GitHub Actions."
    ),
    version="1.0.0",
)


class CalificacionesRequest(BaseModel):
    matricula: str = Field(
        ...,
        json_schema_extra={"example": "20261001"},
        description="Matrícula escolar de 8 dígitos",
    )
    calificaciones: List[float] = Field(
        ...,
        json_schema_extra={"example": [95.0, 92.5, 98.0, 90.0]},
        description="Lista de notas",
    )


class BecaRequest(BaseModel):
    matricula: str = Field(..., json_schema_extra={"example": "20261001"})
    promedio: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 94.5})
    materias_reprobadas: int = Field(0, ge=0, json_schema_extra={"example": 0})
    nivel_socioeconomico: int = Field(3, ge=1, le=5, json_schema_extra={"example": 2})


class InscripcionRequest(BaseModel):
    cuota_base: float = Field(..., gt=0.0, json_schema_extra={"example": 3500.0})
    porcentaje_beca: float = Field(
        ..., ge=0.0, le=100.0, json_schema_extra={"example": 50.0}
    )


@app.get("/", tags=["General"])
def read_root():
    return {
        "sistema": "Sistema Escolar UAdeC - CI/CD Demo",
        "unidad": "3.1 Integración Continua",
        "estado": "Activo y verificado por CI",
        "docs": "/docs",
    }


@app.get("/health", tags=["Salud"])
def health_check():
    """Endpoint de monitoreo de salud del microservicio."""
    return {"status": "ok", "service": "school-ci-service"}


@app.post("/api/v1/promedios", tags=["Calificaciones"])
def endpoint_calcular_promedio(req: CalificacionesRequest):
    if not validar_matricula(req.matricula):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"La matrícula '{req.matricula}' es inválida (debe tener 8 dígitos)."
            ),
        )
    try:
        promedio = calcular_promedio(req.calificaciones)
        return {
            "matricula": req.matricula,
            "materias_evaluadas": len(req.calificaciones),
            "promedio": promedio,
            "aprobado": promedio >= 70.0,
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/v1/becas", tags=["Becas"])
def endpoint_determinar_beca(req: BecaRequest):
    if not validar_matricula(req.matricula):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La matrícula '{req.matricula}' es inválida.",
        )
    try:
        resultado = determinar_estatus_beca(
            promedio=req.promedio,
            materias_reprobadas=req.materias_reprobadas,
            nivel_socioeconomico=req.nivel_socioeconomico,
        )
        return {"matricula": req.matricula, **resultado}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/v1/inscripcion", tags=["Finanzas"])
def endpoint_calcular_inscripcion(req: InscripcionRequest):
    try:
        total = calcular_cuota_final(req.cuota_base, req.porcentaje_beca)
        ahorro = round(req.cuota_base - total, 2)
        return {
            "cuota_base": req.cuota_base,
            "porcentaje_beca": req.porcentaje_beca,
            "monto_descuento": ahorro,
            "total_a_pagar": total,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/v1/auditoria/{matricula}", tags=["Auditoría y Secretos"])
def endpoint_auditoria_academica(matricula: str):
    """Demuestra el uso seguro de secretos en el pipeline de CI.

    El secreto 'ACADEMIC_AUDIT_KEY' se inyecta desde las variables de entorno de CI.
    """
    secret_key = os.environ.get("ACADEMIC_AUDIT_KEY")
    try:
        resultado = consultar_auditoria_academica(matricula, secret_key)
        return resultado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
