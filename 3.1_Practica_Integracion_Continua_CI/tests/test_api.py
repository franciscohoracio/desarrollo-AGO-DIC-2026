"""
Pruebas de Integración de Endpoints REST
UAdeC — Facultad de Sistemas · Unidad 3.1: Integración Continua
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_endpoint_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Sistema Escolar" in data["sistema"]
    assert data["docs"] == "/docs"


def test_endpoint_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "school-ci-service"}


def test_endpoint_promedios_exito():
    payload = {"matricula": "20261001", "calificaciones": [95.0, 90.0, 85.0]}
    response = client.post("/api/v1/promedios", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["promedio"] == 90.0
    assert data["aprobado"] is True
    assert data["materias_evaluadas"] == 3


def test_endpoint_promedios_matricula_invalida():
    payload = {"matricula": "CORTO", "calificaciones": [95.0, 90.0]}
    response = client.post("/api/v1/promedios", json=payload)
    assert response.status_code == 400
    assert "es inválida" in response.json()["detail"]


def test_endpoint_promedios_calificacion_invalida():
    payload = {"matricula": "20261001", "calificaciones": [95.0, 150.0]}
    response = client.post("/api/v1/promedios", json=payload)
    assert response.status_code == 400
    assert "El rango permitido" in response.json()["detail"]


def test_endpoint_becas_exito():
    payload = {
        "matricula": "20261001",
        "promedio": 96.0,
        "materias_reprobadas": 0,
        "nivel_socioeconomico": 2,
    }
    response = client.post("/api/v1/becas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["elegible"] is True
    assert data["porcentaje_beca"] == 100
    assert data["tipo_beca"] == "Excelencia Académica"


def test_endpoint_becas_matricula_invalida():
    payload = {
        "matricula": "INVALIDA",
        "promedio": 90.0,
        "materias_reprobadas": 0,
        "nivel_socioeconomico": 3,
    }
    response = client.post("/api/v1/becas", json=payload)
    assert response.status_code == 400
    assert "es inválida" in response.json()["detail"]


def test_endpoint_inscripcion_exito():
    payload = {"cuota_base": 3000.0, "porcentaje_beca": 50.0}
    response = client.post("/api/v1/inscripcion", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_a_pagar"] == 1500.0
    assert data["monto_descuento"] == 1500.0


def test_endpoint_inscripcion_cuota_negativa():
    payload = {"cuota_base": -100.0, "porcentaje_beca": 50.0}
    # Pydantic validates gt=0.0 -> 422 Unprocessable Entity
    response = client.post("/api/v1/inscripcion", json=payload)
    assert response.status_code == 422


def test_endpoint_auditoria_con_secret_en_entorno(monkeypatch):
    monkeypatch.setenv("ACADEMIC_AUDIT_KEY", "UAdeC-CI-SECRET-KEY-2026")
    response = client.get("/api/v1/auditoria/20261001")
    assert response.status_code == 200
    data = response.json()
    assert data["estatus_auditoria"] == "EXPEDIENTE_VALIDADO"


def test_endpoint_auditoria_sin_secret_falla(monkeypatch):
    monkeypatch.delenv("ACADEMIC_AUDIT_KEY", raising=False)
    response = client.get("/api/v1/auditoria/20261001")
    assert response.status_code == 403
    assert "no configurado o ausente" in response.json()["detail"]


def test_endpoint_auditoria_matricula_invalida(monkeypatch):
    monkeypatch.setenv("ACADEMIC_AUDIT_KEY", "UAdeC-CI-SECRET-KEY-2026")
    response = client.get("/api/v1/auditoria/123")
    assert response.status_code == 400
    assert "no tiene un formato válido" in response.json()["detail"]
