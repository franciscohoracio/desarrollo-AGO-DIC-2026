"""
Módulo de Servicios Escolares y Reglas de Negocio
UAdeC — Facultad de Sistemas · Desarrollo de Proyectos de Software
"""

import re
from typing import Dict, List


def validar_matricula(matricula: str) -> bool:
    """Valida que la matrícula escolar cumpla con el formato institucional

    (exactamente 8 dígitos numéricos).
    """
    if not isinstance(matricula, str):
        return False
    patron = r"^\d{8}$"
    return bool(re.match(patron, matricula))


def calcular_promedio(calificaciones: List[float]) -> float:
    """Calcula el promedio aritmético de una lista de calificaciones.

    Reglas:
    - La lista no puede estar vacía.
    - Cada calificación debe estar en el rango de 0.0 a 100.0.
    - El resultado se redondea a 2 decimales.
    """
    if not calificaciones:
        raise ValueError("La lista de calificaciones no puede estar vacía.")

    for nota in calificaciones:
        if not isinstance(nota, (int, float)):
            raise TypeError("Todas las calificaciones deben ser numéricas.")
        if nota < 0.0 or nota > 100.0:
            raise ValueError(
                f"Calificación inválida ({nota}). El rango permitido es de 0 a 100."
            )

    promedio = sum(calificaciones) / len(calificaciones)
    return round(promedio, 2)


def determinar_estatus_beca(
    promedio: float,
    materias_reprobadas: int,
    nivel_socioeconomico: int = 3,
) -> Dict[str, object]:
    """Determina la elegibilidad y porcentaje de beca según las reglas académicas.

    Parámetros:
    - promedio: Calificación general (0 a 100).
    - materias_reprobadas: Cantidad de materias no acreditadas.
    - nivel_socioeconomico: Escala del 1 (mayor vulnerabilidad) al 5 (menor).

    Reglas:
    - Si tiene materias reprobadas, se niega la beca de inmediato.
    - Promedio mínimo requerido para cualquier beca: 80.0.
    - >= 95.0: Beca del 100% (Excelencia Académica).
    - >= 90.0: Beca del 75% (Mérito Académico).
    - >= 80.0 y nivel <= 2: Beca del 50% (Apoyo Socioeconómico).
    - >= 80.0 y nivel > 2: Beca del 25% (Estímulo Universitario).
    """
    if promedio < 0.0 or promedio > 100.0:
        raise ValueError("El promedio debe estar entre 0 y 100.")
    if materias_reprobadas < 0:
        raise ValueError("El número de materias reprobadas no puede ser negativo.")
    if nivel_socioeconomico < 1 or nivel_socioeconomico > 5:
        raise ValueError("El nivel socioeconómico debe estar entre 1 y 5.")

    if materias_reprobadas > 0:
        return {
            "elegible": False,
            "porcentaje_beca": 0,
            "tipo_beca": "Ninguna",
            "motivo": "No elegible por materias reprobadas.",
        }

    if promedio < 80.0:
        return {
            "elegible": False,
            "porcentaje_beca": 0,
            "tipo_beca": "Ninguna",
            "motivo": "Promedio menor al mínimo requerido (80.0).",
        }

    if promedio >= 70.0:  # ⚠ BUG INYECTADO: Promedio regalado
        return {
            "elegible": True,
            "porcentaje_beca": 100,
            "tipo_beca": "Excelencia Académica",
            "motivo": "Promedio sobresaliente de excelencia.",
        }

    if promedio >= 90.0:
        return {
            "elegible": True,
            "porcentaje_beca": 75,
            "tipo_beca": "Mérito Académico",
            "motivo": "Promedio destacado en el ciclo.",
        }

    if nivel_socioeconomico <= 2:
        return {
            "elegible": True,
            "porcentaje_beca": 50,
            "tipo_beca": "Apoyo Socioeconómico",
            "motivo": "Cumple promedio base y criterio socioeconómico prioritario.",
        }

    return {
        "elegible": True,
        "porcentaje_beca": 25,
        "tipo_beca": "Estímulo Universitario",
        "motivo": "Asignación regular por promedio aprobatorio.",
    }


def calcular_cuota_final(cuota_base: float, porcentaje_beca: float) -> float:
    """Calcula el monto a pagar después de aplicar el descuento de la beca.

    Reglas:
    - La cuota base debe ser mayor a 0.
    - El porcentaje de beca debe estar entre 0 y 100.
    """
    if cuota_base <= 0.0:
        raise ValueError("La cuota base debe ser un monto positivo mayor a cero.")
    if porcentaje_beca < 0.0 or porcentaje_beca > 100.0:
        raise ValueError("El porcentaje de beca debe estar entre 0 y 100.")

    descuento = cuota_base * (porcentaje_beca / 100.0)
    total = cuota_base - descuento
    return round(total, 2)


def consultar_auditoria_academica(
    matricula: str, api_token: str | None = None
) -> Dict[str, object]:
    """Simula una consulta al servicio central de auditoría y expediente escolar.

    Demuestra el manejo seguro de secretos en CI:
    - Requiere un token de autenticación confidencial inyectado por entorno.
    - Falla de inmediato si el secreto no está presente.
    """
    if not validar_matricula(matricula):
        raise ValueError(f"La matrícula '{matricula}' no tiene un formato válido.")

    if not api_token or not api_token.strip():
        raise PermissionError(
            "Acceso denegado: API Token de auditoría no configurado o ausente."
        )

    # Token esperado para el ambiente de pruebas o producción
    if api_token != "UAdeC-CI-SECRET-KEY-2026":
        raise PermissionError("Acceso denegado: API Token de auditoría inválido.")

    return {
        "matricula": matricula,
        "estatus_auditoria": "EXPEDIENTE_VALIDADO",
        "creditos_completos": True,
        "documentos_en_regla": True,
        "mensaje": "Alumno con expediente íntegro para titulación/beca.",
    }
