#!/usr/bin/env bash
# ==============================================================================
# 🧪 LABORATORIO INTERACTIVO DE ESCENARIOS DIDÁCTICOS DE CI
# UAdeC — Facultad de Sistemas · Desarrollo de Proyectos de Software
# Unidad 3.1: Integración Continua (CI)
# ==============================================================================

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Guardar respaldos de seguridad de los archivos originales
mkdir -p "$SCRIPT_DIR/.backup"
cp -r "$SCRIPT_DIR/app" "$SCRIPT_DIR/.backup/"
cp -r "$SCRIPT_DIR/tests" "$SCRIPT_DIR/.backup/"

restaurar_originales() {
    echo -e "${CYAN}Restaurando archivos originales limpios...${NC}"
    cp -r "$SCRIPT_DIR/.backup/app/"* "$SCRIPT_DIR/app/"
    cp -r "$SCRIPT_DIR/.backup/tests/"* "$SCRIPT_DIR/tests/"
    echo -e "${GREEN}✔ Proyecto restaurado al estado limpio (Camino Feliz).${NC}\n"
}

mostrar_menu() {
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BOLD}${CYAN}   🎓 LABORATORIO DIDÁCTICO DE ESCENARIOS DE INTEGRACIÓN CONTINUA (CI)${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "  Experimenta en vivo los conceptos vistos en clase antes de subir a GitHub:"
    echo ""
    echo -e "  ${GREEN}[1]${NC} ${BOLD}Camino Feliz:${NC} Ejecutar Pipeline 100% Sano (Palomita Verde ✅)"
    echo -e "  ${RED}[2]${NC} ${BOLD}Simular Bug en Pruebas:${NC} Error en cálculo de becas (\"Efecto Dominó\") ❌"
    echo -e "  ${RED}[3]${NC} ${BOLD}Simular Infracción de Linter:${NC} Variables huérfanas y descuido de estilo ❌"
    echo -e "  ${RED}[4]${NC} ${BOLD}Simular Caída de Cobertura:${NC} Agregar código sin pruebas (< 85%) ❌"
    echo -e "  ${MAGENTA}[5]${NC} ${BOLD}Simular Manejo de Secretos:${NC} Token faltante vs GitHub Secrets 🔒"
    echo -e "  ${YELLOW}[6]${NC} ${BOLD}Restaurar Proyecto:${NC} Devolver código a su estado original limpio 🔄"
    echo -e "  ${CYAN}[0]${NC} Salir"
    echo -e "${BLUE}==============================================================================${NC}"
    echo -n "Selecciona una opción [0-6]: "
}

while true; do
    mostrar_menu
    read -r opcion
    echo ""

    case "$opcion" in
        1)
            echo -e "${GREEN}${BOLD}--- ESCENARIO 1: EL CAMINO FELIZ (TODO VERDE) ---${NC}"
            echo -e "En este escenario el código está formateado, sin errores de linter,"
            echo -e "con 100% de pruebas aprobadas y cobertura > 90%."
            echo ""
            restaurar_originales
            ./local_ci.sh
            ;;
        2)
            echo -e "${RED}${BOLD}--- ESCENARIO 2: BUG DE REGRESIÓN (EL EFECTO DOMINÓ) ---${NC}"
            echo -e "${YELLOW}Explicación didáctica:${NC}"
            echo -e "Un desarrollador modificó la función 'determinar_estatus_beca' para dar"
            echo -e "100% de beca a quien tenga promedio > 70 por error."
            echo ""
            restaurar_originales
            
            # Inyectar bug en app/school_service.py
            sed -i '' 's/if promedio >= 95.0:/if promedio >= 70.0:  # ⚠ BUG INYECTADO: Promedio regalado/g' app/school_service.py 2>/dev/null || \
            sed -i 's/if promedio >= 95.0:/if promedio >= 70.0:  # ⚠ BUG INYECTADO: Promedio regalado/g' app/school_service.py
            
            echo -e "${RED}Bug inyectado en app/school_service.py.${NC} Ejecutando CI para ver cómo reacciona el robot..."
            echo ""
            ./local_ci.sh || true
            echo -e "${YELLOW}💡 ¿Qué aprendimos?: Las pruebas unitarias detectaron el fallo en milisegundos."
            echo -e "   En GitHub, el botón 'Merge' se desactiva y el código roto NUNCA entra a main.${NC}\n"
            ;;
        3)
            echo -e "${RED}${BOLD}--- ESCENARIO 3: INFRACCIÓN DE LINTER Y ESTILO ---${NC}"
            echo -e "${YELLOW}Explicación didáctica:${NC}"
            echo -e "Un desarrollador dejó variables que nunca usó y formatos descuidados."
            echo -e "El linter (Flake8) y formateador (Black) actúan como el corrector ortográfico."
            echo ""
            restaurar_originales

            # Inyectar error de linter
            echo -e "\n\n# ⚠ Codigo descuidado inyectado\nvariable_inutil = 'nadie me usa'\ndef funcion_fea( a , b ):\n    total=a+b\n    return total\n" >> app/school_service.py

            echo -e "${RED}Código sucio inyectado en app/school_service.py.${NC} Ejecutando CI..."
            echo ""
            ./local_ci.sh || true
            echo -e "${YELLOW}💡 ¿Qué aprendimos?: Flake8 detuvo la banda de ensamblaje antes de las pruebas."
            echo -e "   Esto evita peleas de estilo y previene errores tipográficos en el equipo.${NC}\n"
            ;;
        4)
            echo -e "${RED}${BOLD}--- ESCENARIO 4: VIOLACIÓN DEL QUALITY GATE (COBERTURA < 85%) ---${NC}"
            echo -e "${YELLOW}Explicación didáctica:${NC}"
            echo -e "Un programador agregó un módulo nuevo de 60 líneas pero 'olvidó' hacerle pruebas."
            echo -e "El Quality Gate configurado en 85% bloqueará el commit de inmediato."
            echo ""
            restaurar_originales

            # Inyectar funciones con formato y linter impecables, pero sin pruebas unitarias
            cat << 'EOF' >> app/school_service.py


def calcular_estadisticas_avanzadas(datos_alumnos: list) -> dict:
    """Función de analítica institucional agregada sin pruebas unitarias."""
    total = len(datos_alumnos)
    if total == 0:
        return {"media": 0.0, "mediana": 0.0, "moda": 0.0, "desviacion": 0.0}

    suma = 0.0
    for elemento in datos_alumnos:
        if elemento > 0:
            suma += elemento
        else:
            suma += 0.0

    promedio = suma / total
    varianza = 0.0
    for elemento in datos_alumnos:
        diferencia = elemento - promedio
        varianza += diferencia**2

    desviacion = (varianza / total) ** 0.5
    return {
        "media": round(promedio, 2),
        "varianza": round(varianza, 2),
        "desviacion": round(desviacion, 2),
        "total": total,
    }


def generar_reporte_financiero_patronatos(cuotas: list) -> dict:
    """Función de tesorería institucional sin pruebas unitarias."""
    ingresos = 0.0
    descuentos = 0.0
    for item in cuotas:
        monto = item.get("monto", 0.0)
        descuento = item.get("descuento", 0.0)
        ingresos += monto
        descuentos += descuento

    neto = ingresos - descuentos
    factor = 1.0
    if neto > 100000:
        factor = 0.95
    elif neto > 50000:
        factor = 0.98

    return {
        "ingresos_brutos": ingresos,
        "descuentos_totales": descuentos,
        "ingresos_netos": neto * factor,
    }
EOF
            echo -e "${RED}Código nuevo sin pruebas unitarias inyectado.${NC} Ejecutando CI..."
            echo ""
            ./local_ci.sh || true
            echo -e "${YELLOW}💡 ¿Qué aprendimos?: Aunque las pruebas existentes pasaron, la cobertura global"
            echo -e "   cayó y el Quality Gate detuvo el pipeline por falta de rigor.${NC}\n"
            ;;
        5)
            echo -e "${MAGENTA}${BOLD}--- ESCENARIO 5: SEGURIDAD Y GITHUB SECRETS ---${NC}"
            echo -e "${YELLOW}Explicación didáctica:${NC}"
            echo -e "En CI nunca subimos contraseñas al código. Se inyectan en memoria segura."
            echo -e "Veamos qué ocurre si ejecutamos el pipeline SIN el secreto configurado:"
            echo ""
            restaurar_originales
            ./local_ci.sh --sin-secreto || true
            echo -e "${YELLOW}💡 ¿Qué aprendimos?: Sin la variable inyectada, el pipeline rechaza el despliegue."
            echo -e "   Al configurarla en Settings -> Secrets de GitHub, se inyecta de forma cifrada.${NC}\n"
            ;;
        6)
            restaurar_originales
            ;;
        0)
            echo -e "${CYAN}Restaurando archivos y saliendo...${NC}"
            restaurar_originales
            rm -rf "$SCRIPT_DIR/.backup"
            echo -e "${GREEN}¡Hasta luego! Recuerda: Main siempre debe estar en VERDE.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida. Intenta nuevamente.${NC}\n"
            ;;
    esac

    echo -e "${BOLD}Presiona ENTER para continuar...${NC}"
    read -r
done
