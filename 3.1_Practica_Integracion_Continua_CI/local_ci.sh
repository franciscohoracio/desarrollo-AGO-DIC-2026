#!/usr/bin/env bash
# ==============================================================================
# 🚀 SIMULADOR LOCAL DEL PIPELINE DE INTEGRACIÓN CONTINUA (CI)
# UAdeC — Facultad de Sistemas · Desarrollo de Proyectos de Software
# Unidad 3.1: Integración Continua (CI)
# ==============================================================================
# Este script replica localmente la ejecución exacta que realiza GitHub Actions
# en el runner en la nube (ubuntu-latest), permitiendo verificar tu código
# ANTES de hacer git push y proteger la rama principal (main).
# ==============================================================================

set -o pipefail

# Colores y estilos
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detección del ejecutable de Python / Entorno Virtual
PYTHON_BIN="python3"
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
fi

START_TOTAL=$(date +%s)
FAILED_STEPS=()

imprimir_banner() {
    clear 2>/dev/null || true
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BOLD}${CYAN}   🏭 SIMULADOR LOCAL DEL PIPELINE DE INTEGRACIÓN CONTINUA (CI)${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "  ${YELLOW}Materia:${NC} Desarrollo de Proyectos de Software · UAdeC"
    echo -e "  ${YELLOW}Unidad:${NC}  3.1 Integración Continua (CI) y Automatización de Pipelines"
    echo -e "  ${YELLOW}Runner:${NC}  Simulador Local (Equivalente a ubuntu-latest en GitHub Actions)"
    echo -e "  ${YELLOW}Python:${NC}  $($PYTHON_BIN --version 2>&1)"
    echo -e "${BLUE}==============================================================================${NC}\n"
}

ejecutar_paso() {
    local num="$1"
    local nombre="$2"
    local comando="$3"

    echo -e "${BOLD}${CYAN}▶ Paso $num: $nombre${NC}"
    echo -e "${YELLOW}  Comando:${NC} \`$comando\`"
    
    local start_step=$(date +%s)
    eval "$comando"
    local exit_code=$?
    local end_step=$(date +%s)
    local duracion=$((end_step - start_step))

    if [ $exit_code -eq 0 ]; then
        echo -e "  ${GREEN}✔ APROBADO${NC} (${duracion}s)\n"
    else
        echo -e "  ${RED}✖ FALLÓ (Código de salida: $exit_code)${NC} (${duracion}s)\n"
        FAILED_STEPS+=("Paso $num: $nombre")
        return $exit_code
    fi
}

imprimir_banner

# Inyectar secreto simulado si no existe en el entorno
export ACADEMIC_AUDIT_KEY="${ACADEMIC_AUDIT_KEY:-UAdeC-CI-SECRET-KEY-2026}"

echo -e "${BOLD}Iniciando banda de ensamblaje y control de calidad...${NC}\n"

# 1. Verificación de Dependencias
ejecutar_paso 1 "Verificación de dependencias instaladas" \
    "$PYTHON_BIN -c 'import fastapi, pytest, pytest_cov, flake8, black; print(\"  Librerías principales listas en el entorno.\")'" || true

# 2. Formateador Estricto (Black)
ejecutar_paso 2 "Formateador de código (Black) — Consistencia de estilo" \
    "$PYTHON_BIN -m black --check --diff app tests" || true

# 3. Linter y Análisis Estático (Flake8)
ejecutar_paso 3 "Linter y Análisis Estático (Flake8) — Detección de bugs y variables huérfanas" \
    "$PYTHON_BIN -m flake8 app tests" || true

# 4. Manejo Seguro de Secretos
ejecutar_paso 4 "Verificación de Secretos (Simulación de GitHub Secrets)" \
    "$PYTHON_BIN -c '
import os, sys
token = os.environ.get(\"ACADEMIC_AUDIT_KEY\")
if not token:
    print(\"  ❌ ERROR: El secreto ACADEMIC_AUDIT_KEY no está presente en el entorno.\")
    sys.exit(1)
print(f\"  ✅ Secreto inyectado en memoria segura: [***{token[-4:]}]\")
print(\"  (Nota didáctica: GitHub censura secretos en consola para evitar filtraciones)\")
'" || true

# 5. Pruebas Unitarias y Quality Gate de Cobertura
ejecutar_paso 5 "Pruebas Unitarias y Quality Gate (Pytest + Cobertura >= 85%)" \
    "$PYTHON_BIN -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=85" || true

# Resumen Final
END_TOTAL=$(date +%s)
DURACION_TOTAL=$((END_TOTAL - START_TOTAL))

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BOLD}                     📊 RESUMEN FINAL DEL PIPELINE${NC}"
echo -e "${BLUE}==============================================================================${NC}"
echo -e "  Tiempo total de ejecución: ${BOLD}${DURACION_TOTAL} segundos${NC} (Objetivo: < 300s)"

if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    echo -e "\n  ${GREEN}${BOLD}===================================================================${NC}"
    echo -e "  ${GREEN}${BOLD}  ✅ VEREDICTO: PASSED (TODO EN VERDE)                            ${NC}"
    echo -e "  ${GREEN}${BOLD}  Tu código cumple con todos los estándares de calidad.           ${NC}"
    echo -e "  ${GREEN}${BOLD}  Puedes abrir tu Pull Request o hacer merge con tranquilidad.     ${NC}"
    echo -e "  ${GREEN}${BOLD}===================================================================${NC}\n"
    exit 0
else
    echo -e "\n  ${RED}${BOLD}===================================================================${NC}"
    echo -e "  ${RED}${BOLD}  ❌ VEREDICTO: FAILED (PIPELINE EN ROJO)                         ${NC}"
    echo -e "  ${RED}${BOLD}  Se detectaron errores en los siguientes pasos:                   ${NC}"
    for paso in "${FAILED_STEPS[@]}"; do
        echo -e "  ${RED}    - $paso${NC}"
    done
    echo -e "  ${RED}${BOLD}-------------------------------------------------------------------${NC}"
    echo -e "  ${YELLOW}💡 Consejo de Oro: En un equipo profesional, arreglar un build en rojo"
    echo -e "     es la prioridad #1. Nadie fusiona código a 'main' hasta corregirlo.${NC}"
    echo -e "  ${RED}${BOLD}===================================================================${NC}\n"
    exit 1
fi
