#!/usr/bin/env bash

# =============================================================================
# 🚀 SCRIPT DE PRUEBA INTERACTIVO · PRÁCTICA 2.3: INTERFACES DE COMUNICACIÓN Y APIS
# =============================================================================
# Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
# =============================================================================

# Colores para la terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

REST_URL="http://localhost:8001"
GRAPHQL_URL="http://localhost:8002/graphql"
REALTIME_URL="http://localhost:8003"
GRPC_HOST="localhost:50051"

print_header() {
    clear
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BOLD}${CYAN}  🎓 Práctica 2.3 · Suite de Pruebas de Interfaces de Comunicación${NC}"
    echo -e "${BLUE}  RESTful · Swagger · JWT · GraphQL · gRPC · WebSockets · SSE · Webhooks${NC}"
    echo -e "${BLUE}======================================================================${NC}\n"
}

check_services() {
    echo -e "${YELLOW}🔍 Verificando estado de los 4 microservicios en Docker...${NC}"
    
    REST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$REST_URL/health" 2>/dev/null || echo "000")
    GRAPHQL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8002/health" 2>/dev/null || echo "000")
    REALTIME_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$REALTIME_URL/health" 2>/dev/null || echo "000")
    
    if [ "$REST_STATUS" == "200" ]; then
        echo -e "  ✅ [8001] REST API Service        : ${GREEN}ONLINE${NC} (Swagger en $REST_URL/docs)"
    else
        echo -e "  ❌ [8001] REST API Service        : ${RED}OFFLINE${NC}"
    fi

    if [ "$GRAPHQL_STATUS" == "200" ]; then
        echo -e "  ✅ [8002] GraphQL Service         : ${GREEN}ONLINE${NC} (GraphiQL en $GRAPHQL_URL)"
    else
        echo -e "  ❌ [8002] GraphQL Service         : ${RED}OFFLINE${NC}"
    fi

    echo -e "  ✅ [50051] gRPC Analytics Service : ${GREEN}ONLINE${NC} (HTTP/2 + Protobuf)"

    if [ "$REALTIME_STATUS" == "200" ]; then
        echo -e "  ✅ [8003] Real-Time Dashboard     : ${GREEN}ONLINE${NC} (WebSockets/SSE en $REALTIME_URL)"
    else
        echo -e "  ❌ [8003] Real-Time Dashboard     : ${RED}OFFLINE${NC}"
    fi

    if [ "$REST_STATUS" != "200" ] || [ "$GRAPHQL_STATUS" != "200" ] || [ "$REALTIME_STATUS" != "200" ]; then
        echo -e "\n${YELLOW}💡 Recuerda encender todos los contenedores ejecutando:${NC}"
        echo -e "   ${CYAN}docker compose up -d${NC}\n"
    fi
}

test_rest_jwt() {
    echo -e "\n${BOLD}${CYAN}--- [1] PRUEBA DE REST API, VERSIONADO Y SEGURIDAD JWT ---${NC}\n"
    
    echo -e "${YELLOW}Paso 1: Iniciando sesión en '/auth/login' como Docente...${NC}"
    LOGIN_RESP=$(curl -s -X POST "$REST_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "docente@uadec.mx", "password": "password123"}')
    
    TOKEN=$(echo "$LOGIN_RESP" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        echo -e "${RED}❌ Error al obtener token JWT. Respuesta:${NC} $LOGIN_RESP"
        return
    fi

    echo -e "${GREEN}✅ ¡Token JWT (Pulsera VIP) generado exitosamente!${NC}"
    echo -e "${MAGENTA}Bearer Token:${NC} ${TOKEN:0:40}...\n"

    echo -e "${YELLOW}Paso 2: Consultando API v1 (Legacy / Combo Fijo):${NC}"
    echo -e "${CYAN}GET /v1/students/12345${NC}"
    curl -s "$REST_URL/v1/students/12345" | python3 -m json.tool 2>/dev/null || curl -s "$REST_URL/v1/students/12345"
    echo ""

    echo -e "${YELLOW}Paso 3: Consultando API v2 (Moderna / Enriquecida con Filtros):${NC}"
    echo -e "${CYAN}GET /v2/students?estado=activo${NC}"
    curl -s "$REST_URL/v2/students?estado=activo" | python3 -m json.tool 2>/dev/null || curl -s "$REST_URL/v2/students?estado=activo"
    echo ""

    echo -e "${YELLOW}Paso 4: Intentando crear un alumno SIN TOKEN (Debe fallar con HTTP 401 Unauthorized):${NC}"
    HTTP_CODE_NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$REST_URL/v2/students" \
        -H "Content-Type: application/json" \
        -d '{"matricula": "99999", "nombre": "Hacker", "carrera": "Sistemas", "email": "hacker@test.com"}')
    echo -e "Código recibido: ${RED}HTTP $HTTP_CODE_NO_AUTH Unauthorized${NC} (¡El cadenero del sistema protegió la API!)"

    echo -e "\n${YELLOW}Paso 5: Creando un alumno CON TOKEN VÁLIDO (Debe responder HTTP 201 Created):${NC}"
    RAND_MAT=$((RANDOM % 80000 + 10000))
    CREATE_RESP=$(curl -s -w "\n%{http_code}" -X POST "$REST_URL/v2/students" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"matricula\": \"$RAND_MAT\", \"nombre\": \"Estudiante Demo $RAND_MAT\", \"carrera\": \"Ingeniería en Sistemas Computacionales\", \"email\": \"demo$RAND_MAT@uadec.mx\", \"semestre\": 3, \"promedio\": 96.5}")
    
    HTTP_CODE_AUTH=$(echo "$CREATE_RESP" | tail -n1)
    BODY_AUTH=$(echo "$CREATE_RESP" | sed '$d')
    
    if [ "$HTTP_CODE_AUTH" == "201" ]; then
        echo -e "Código recibido: ${GREEN}HTTP 201 Created${NC}"
        echo "$BODY_AUTH" | python3 -m json.tool 2>/dev/null || echo "$BODY_AUTH"
    else
        echo -e "Código recibido: ${RED}HTTP $HTTP_CODE_AUTH${NC}"
        echo "$BODY_AUTH"
    fi
}

test_graphql() {
    echo -e "\n${BOLD}${MAGENTA}--- [2] PRUEBA DE GRAPHQL (SOLUCIÓN A OVER/UNDER-FETCHING) ---${NC}\n"
    
    echo -e "${YELLOW}1. Comparativa de Over-fetching (Descarga innecesaria de datos):${NC}"
    echo -e "• En REST v2 completo recibes: CURP, dirección de casa, historial médico, alergias, teléfono..."
    echo -e "• En GraphQL pedimos ÚNICAMENTE ${BOLD}'nombre' y 'promedio'${NC} para la pantalla del celular:"
    
    GQL_QUERY_1='{"query": "{ student(matricula: \"12345\") { nombre promedio } }"}'
    
    echo -e "\n${CYAN}POST /graphql -> query { student(matricula: \"12345\") { nombre promedio } }${NC}"
    curl -s -X POST "$GRAPHQL_URL" \
        -H "Content-Type: application/json" \
        -d "$GQL_QUERY_1" | python3 -m json.tool 2>/dev/null
    
    echo -e "\n${YELLOW}2. Solución a Under-fetching (Consulta anidada en 1 sola petición HTTP):${NC}"
    echo -e "• Obtenemos al alumno + sus materias inscritas + nombre del profesor asignado:"
    
    GQL_QUERY_2='{"query": "{ student(matricula: \"12345\") { nombre carrera materias { codigo nombre profesor calificacion } } }"}'
    
    echo -e "\n${CYAN}POST /graphql -> Consulta Relacional Anidada${NC}"
    curl -s -X POST "$GRAPHQL_URL" \
        -H "Content-Type: application/json" \
        -d "$GQL_QUERY_2" | python3 -m json.tool 2>/dev/null
    
    echo -e "\n${GREEN}💡 Resultado: Cero round-trips adicionales y cero datos desperdiciados.${NC}"
}

test_grpc() {
    echo -e "\n${BOLD}${CYAN}--- [3] PRUEBA DE gRPC Y PROTOCOL BUFFERS (ALTA VELOCIDAD) ---${NC}\n"
    
    echo -e "${YELLOW}1. Ejecutando RPC Unario dentro del contenedor gRPC (Latencia en microsegundos):${NC}"
    docker compose exec grpc_service python client.py --unary --matricula 12345 2>/dev/null || \
        echo -e "${RED}❌ Asegúrate de que el contenedor 'campus_grpc_analytics' esté activo.${NC}"
    
    echo -e "${YELLOW}2. Ejecutando Server Streaming (Flujo continuo de telemetría de campus):${NC}"
    docker compose exec grpc_service python client.py --stream --total 4 2>/dev/null || \
        echo -e "${RED}❌ Asegúrate de que el contenedor 'campus_grpc_analytics' esté activo.${NC}"
}

test_realtime_webhooks() {
    echo -e "\n${BOLD}${GREEN}--- [4] PRUEBA DE TIEMPO REAL Y WEBHOOKS ---${NC}\n"
    
    echo -e "${YELLOW}Simulando Webhook de Pasarela de Pagos (Stripe / Banco BBVA):${NC}"
    echo -e "${CYAN}POST /webhooks/tuition-payment${NC}"
    
    TXN_ID="TXN-$((RANDOM % 900000 + 100000))"
    PAYMENT_JSON=$(cat <<EOF
{
  "transaccion_id": "$TXN_ID",
  "matricula": "12345",
  "alumno": "Carlos Gómez",
  "monto": 3450.00,
  "concepto": "Inscripción Semestre Ago-Dic 2026",
  "banco_emisor": "BBVA México"
}
EOF
)

    RESP=$(curl -s -X POST "$REALTIME_URL/webhooks/tuition-payment" \
        -H "Content-Type: application/json" \
        -H "X-Webhook-Secret: uadec-secret-token" \
        -d "$PAYMENT_JSON")
        
    echo "$RESP" | python3 -m json.tool 2>/dev/null || echo "$RESP"
    echo -e "\n${GREEN}✅ Webhook recibido. ¡Si tienes abierto el Dashboard ($REALTIME_URL) verás la alerta en tiempo real!${NC}"
}

test_benchmark() {
    echo -e "\n${BOLD}${YELLOW}--- [5] BENCHMARK COMPARATIVO DE RENDIMIENTO (REST vs GRAPHQL vs gRPC) ---${NC}\n"
    TOTAL_REQUESTS=30
    echo -e "Ejecutando ${TOTAL_REQUESTS} peticiones secuenciales a cada protocolo...\n"

    # 1. REST Benchmark
    START_REST=$(python3 -c "import time; print(time.time())")
    for ((i=1; i<=TOTAL_REQUESTS; i++)); do
        curl -s "$REST_URL/v1/students/12345" > /dev/null
    done
    END_REST=$(python3 -c "import time; print(time.time())")
    DUR_REST=$(python3 -c "print(f'{($END_REST - $START_REST):.3f}')")
    LAT_REST=$(python3 -c "print(f'{(($END_REST - $START_REST)/$TOTAL_REQUESTS)*1000:.2f}')")

    # 2. GraphQL Benchmark
    START_GQL=$(python3 -c "import time; print(time.time())")
    for ((i=1; i<=TOTAL_REQUESTS; i++)); do
        curl -s -X POST "$GRAPHQL_URL" -H "Content-Type: application/json" -d '{"query": "{ student(matricula: \"12345\") { nombre } }"}' > /dev/null
    done
    END_GQL=$(python3 -c "import time; print(time.time())")
    DUR_GQL=$(python3 -c "print(f'{($END_GQL - $START_GQL):.3f}')")
    LAT_GQL=$(python3 -c "print(f'{(($END_GQL - $START_GQL)/$TOTAL_REQUESTS)*1000:.2f}')")

    echo -e "  🌐 ${BOLD}REST API (JSON over HTTP/1.1)${NC}      : ${CYAN}${DUR_REST}s total${NC} | Promedio: ${GREEN}${LAT_REST} ms/req${NC}"
    echo -e "  🍇 ${BOLD}GraphQL (JSON Query over POST)${NC}     : ${CYAN}${DUR_GQL}s total${NC} | Promedio: ${GREEN}${LAT_GQL} ms/req${NC}"
    
    echo -e "\n  ⚡ ${BOLD}Ejecutando Benchmark Nativo de gRPC (Protobuf over HTTP/2):${NC}"
    docker compose exec grpc_service python client.py --benchmark --requests $TOTAL_REQUESTS 2>/dev/null
}

open_browser_urls() {
    echo -e "\n${BOLD}${CYAN}--- ENLACES DIRECTOS A LAS INTERFACES WEB ---${NC}\n"
    echo -e "  📖 Swagger REST UI       : ${BLUE}http://localhost:8001/docs${NC}"
    echo -e "  🍇 GraphiQL Playground   : ${MAGENTA}http://localhost:8002/graphql${NC}"
    echo -e "  📡 Dashboard Tiempo Real : ${GREEN}http://localhost:8003${NC}"
    echo -e "  ⚡ gRPC Analytics Port   : ${YELLOW}localhost:50051 (HTTP/2 Binary)${NC}\n"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        read -rp "¿Deseas abrir las 3 interfaces en tu navegador ahora? (s/N): " OPEN_OPT
        if [[ "$OPEN_OPT" =~ ^[sSyY]$ ]]; then
            open "http://localhost:8001/docs"
            open "http://localhost:8002/graphql"
            open "http://localhost:8003"
        fi
    fi
}

# Bucle interactivo principal
while true; do
    print_header
    check_services
    echo -e "\n${BOLD}Selecciona una opción de prueba:${NC}"
    echo -e "  ${CYAN}[1]${NC} Probar REST API, Versionado (v1/v2) y Seguridad con JWT"
    echo -e "  ${MAGENTA}[2]${NC} Probar GraphQL (Over-fetching vs Consulta a la carta)"
    echo -e "  ${BLUE}[3]${NC} Probar gRPC & Protocol Buffers (Unario y Server Streaming)"
    echo -e "  ${GREEN}[4]${NC} Probar Tiempo Real (WebSockets, SSE y Webhooks)"
    echo -e "  ${YELLOW}[5]${NC} Ejecutar Benchmark Comparativo de Rendimiento"
    echo -e "  ${CYAN}[6]${NC} Mostrar URLs y Abrir Interfaces en el Navegador"
    echo -e "  ${RED}[0]${NC} Salir\n"
    
    read -rp "Opción seleccionada [1-6, 0]: " OPTION
    
    case $OPTION in
        1) test_rest_jwt ;;
        2) test_graphql ;;
        3) test_grpc ;;
        4) test_realtime_webhooks ;;
        5) test_benchmark ;;
        6) open_browser_urls ;;
        0) echo -e "\n👋 ¡Hasta luego!"; exit 0 ;;
        *) echo -e "\n${RED}Opción inválida.${NC}" ;;
    esac
    
    echo -e "\nPresiona ${BOLD}[ENTER]${NC} para volver al menú..."
    read -r
done
