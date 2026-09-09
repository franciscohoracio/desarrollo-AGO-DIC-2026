"""
Pruebas Unitarias de la Lógica de Negocio Escolar
UAdeC — Facultad de Sistemas · Unidad 3.1: Integración Continua
"""

import pytest
from app.school_service import (
    validar_matricula,
    calcular_promedio,
    determinar_estatus_beca,
    calcular_cuota_final,
    consultar_auditoria_academica,
)


class TestValidarMatricula:
    def test_matricula_valida(self):
        assert validar_matricula("20261001") is True
        assert validar_matricula("12345678") is True

    def test_matricula_invalida_longitud(self):
        assert validar_matricula("1234567") is False  # 7 dígitos
        assert validar_matricula("123456789") is False  # 9 dígitos

    def test_matricula_con_letras_o_simbolos(self):
        assert validar_matricula("2026ABCD") is False
        assert validar_matricula("2026-100") is False

    def test_matricula_tipo_invalido(self):
        assert validar_matricula(None) is False
        assert validar_matricula(20261001) is False


class TestCalcularPromedio:
    def test_promedio_valores_validos(self):
        notas = [90.0, 95.0, 85.0]
        assert calcular_promedio(notas) == 90.0

    def test_promedio_redondeo_dos_decimales(self):
        notas = [100.0, 95.0, 92.0]
        # (100 + 95 + 92) / 3 = 95.6666... -> 95.67
        assert calcular_promedio(notas) == 95.67

    def test_promedio_lista_vacia(self):
        with pytest.raises(ValueError, match="no puede estar vacía"):
            calcular_promedio([])

    def test_promedio_calificacion_fuera_de_rango(self):
        with pytest.raises(ValueError, match="El rango permitido es de 0 a 100"):
            calcular_promedio([90.0, 105.0])

        with pytest.raises(ValueError, match="El rango permitido es de 0 a 100"):
            calcular_promedio([-5.0, 80.0])

    def test_promedio_elemento_no_numerico(self):
        with pytest.raises(TypeError, match="deben ser numéricas"):
            calcular_promedio([90.0, "cien"])


class TestDeterminarEstatusBeca:
    def test_beca_excelencia_100(self):
        resultado = determinar_estatus_beca(
            promedio=96.0, materias_reprobadas=0, nivel_socioeconomico=3
        )
        assert resultado["elegible"] is True
        assert resultado["porcentaje_beca"] == 100
        assert resultado["tipo_beca"] == "Excelencia Académica"

    def test_beca_merito_75(self):
        resultado = determinar_estatus_beca(
            promedio=91.5, materias_reprobadas=0, nivel_socioeconomico=4
        )
        assert resultado["elegible"] is True
        assert resultado["porcentaje_beca"] == 75
        assert resultado["tipo_beca"] == "Mérito Académico"

    def test_beca_socioeconomica_50(self):
        resultado = determinar_estatus_beca(
            promedio=85.0, materias_reprobadas=0, nivel_socioeconomico=2
        )
        assert resultado["elegible"] is True
        assert resultado["porcentaje_beca"] == 50
        assert resultado["tipo_beca"] == "Apoyo Socioeconómico"

    def test_beca_estimulo_25(self):
        resultado = determinar_estatus_beca(
            promedio=84.0, materias_reprobadas=0, nivel_socioeconomico=4
        )
        assert resultado["elegible"] is True
        assert resultado["porcentaje_beca"] == 25
        assert resultado["tipo_beca"] == "Estímulo Universitario"

    def test_no_elegible_por_materias_reprobadas(self):
        resultado = determinar_estatus_beca(
            promedio=98.0, materias_reprobadas=1, nivel_socioeconomico=1
        )
        assert resultado["elegible"] is False
        assert resultado["porcentaje_beca"] == 0
        assert "reprobadas" in resultado["motivo"]

    def test_no_elegible_por_promedio_bajo(self):
        resultado = determinar_estatus_beca(
            promedio=78.5, materias_reprobadas=0, nivel_socioeconomico=1
        )
        assert resultado["elegible"] is False
        assert resultado["porcentaje_beca"] == 0
        assert "Promedio menor al mínimo" in resultado["motivo"]

    def test_validaciones_parametros_invalidos(self):
        with pytest.raises(ValueError, match="El promedio debe estar entre 0 y 100"):
            determinar_estatus_beca(promedio=105.0, materias_reprobadas=0)

        with pytest.raises(
            ValueError, match="materias reprobadas no puede ser negativo"
        ):
            determinar_estatus_beca(promedio=90.0, materias_reprobadas=-1)

        with pytest.raises(
            ValueError, match="nivel socioeconómico debe estar entre 1 y 5"
        ):
            determinar_estatus_beca(
                promedio=90.0, materias_reprobadas=0, nivel_socioeconomico=6
            )


class TestCalcularCuotaFinal:
    def test_descuento_completo_beca_100(self):
        assert calcular_cuota_final(cuota_base=4000.0, porcentaje_beca=100.0) == 0.0

    def test_descuento_parcial_beca_50(self):
        assert calcular_cuota_final(cuota_base=3500.0, porcentaje_beca=50.0) == 1750.0

    def test_sin_beca_cero_descuento(self):
        assert calcular_cuota_final(cuota_base=2500.0, porcentaje_beca=0.0) == 2500.0

    def test_cuota_invalida_menor_o_igual_a_cero(self):
        with pytest.raises(ValueError, match="cuota base debe ser un monto positivo"):
            calcular_cuota_final(cuota_base=0.0, porcentaje_beca=50.0)

    def test_porcentaje_beca_invalido(self):
        with pytest.raises(ValueError, match="debe estar entre 0 y 100"):
            calcular_cuota_final(cuota_base=3000.0, porcentaje_beca=120.0)


class TestAuditoriaAcademicaYSecretos:
    def test_auditoria_con_token_valido(self):
        token_correcto = "UAdeC-CI-SECRET-KEY-2026"
        res = consultar_auditoria_academica("20261001", api_token=token_correcto)
        assert res["estatus_auditoria"] == "EXPEDIENTE_VALIDADO"
        assert res["creditos_completos"] is True

    def test_auditoria_sin_token_falla(self):
        with pytest.raises(PermissionError, match="no configurado o ausente"):
            consultar_auditoria_academica("20261001", api_token=None)

    def test_auditoria_con_token_invalido_falla(self):
        with pytest.raises(PermissionError, match="Token de auditoría inválido"):
            consultar_auditoria_academica("20261001", api_token="TOKEN_EQUIVOCADO")

    def test_auditoria_matricula_invalida(self):
        with pytest.raises(ValueError, match="no tiene un formato válido"):
            consultar_auditoria_academica("MATRICULA_ROTA", api_token="CUALQUIERA")
