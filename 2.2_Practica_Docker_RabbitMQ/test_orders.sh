#!/usr/bin/env bash

# Script de prueba interactivo para la Práctica 2.2
# Envía N pedidos aleatorios a la API de Orders

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  Práctica 2.2 · Pipeline Asíncrono con RabbitMQ      ${NC}"
echo -e "${BLUE}======================================================${NC}\n"

# 1. Verificar si la API responde
echo -e "${YELLOW}🔍 Verificando salud de Orders API y RabbitMQ...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" || echo "000")

if [ "$HEALTH_RESPONSE" != "200" ]; then
    echo -e "❌ Error: La API no responde en $API_URL/health (HTTP $HEALTH_RESPONSE)"
    echo -e "💡 Asegúrate de haber iniciado los contenedores con: ${CYAN}docker compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Orders API y RabbitMQ están saludables y listos.${NC}\n"

# 2. Preguntar cuántos pedidos enviar (o tomar argumento de línea de comandos)
if [ -n "$1" ]; then
    TOTAL_ORDERS=$1
else
    read -rp "📦 ¿Cuántos pedidos deseas enviar? (ej. 5, 10, 50) [10]: " INPUT_ORDERS
    TOTAL_ORDERS=${INPUT_ORDERS:-10}
fi

# Validar que sea un número entero positivo
if ! [[ "$TOTAL_ORDERS" =~ ^[0-9]+$ ]] || [ "$TOTAL_ORDERS" -le 0 ]; then
    echo -e "${RED}❌ Error: Debes ingresar un número entero mayor a 0.${NC}"
    exit 1
fi

echo -e "\n${CYAN}🚀 Iniciando envío de ${TOTAL_ORDERS} pedidos con datos aleatorios...${NC}\n"

# Catálogo de datos aleatorios
ITEMS=(
  "Laptop Gamer Ryzen 7"
  "MacBook Pro M3"
  "Teclado Mecánico RGB"
  "Monitor 4K 27 pulgadas"
  "Mouse Ergonómico Inalámbrico"
  "Silla Ergonómica Gamer"
  "Auriculares Bluetooth ANC"
  "Tarjeta Gráfica RTX 4070"
  "Micrófono USB Podcast"
  "Webcam 4K UltraHD"
  "Disco SSD NVMe 2TB"
  "Memoria RAM DDR5 32GB"
  "Smartwatch Deportivo"
  "Tablet OLED 11 pulgadas"
  "Docking Station Thunderbolt 4"
  "Hub USB-C 7 en 1"
)

USERS=(
  "ana.garcia"
  "carlos.lopez"
  "maria.torres"
  "juan.perez"
  "laura.hernandez"
  "rodrigo.sanchez"
  "sofia.castro"
  "diego.ramirez"
  "valeria.morales"
  "fernando.gomez"
  "paola.vargas"
  "mateo.diaz"
  "alberto.ruiz"
  "lucia.mendoza"
  "gabriel.navarro"
)

DOMAINS=("uadec.mx" "gmail.com" "outlook.com" "proton.me" "innovasolutions.io")

ITEMS_COUNT=${#ITEMS[@]}
USERS_COUNT=${#USERS[@]}
DOMAINS_COUNT=${#DOMAINS[@]}

SUCCESS_COUNT=0
START_TIME=$(date +%s)

for ((i=1; i<=TOTAL_ORDERS; i++)); do
    RAND_ITEM=${ITEMS[$((RANDOM % ITEMS_COUNT))]}
    RAND_USER=${USERS[$((RANDOM % USERS_COUNT))]}
    RAND_DOMAIN=${DOMAINS[$((RANDOM % DOMAINS_COUNT))]}
    RAND_EMAIL="${RAND_USER}${RANDOM:0:2}@${RAND_DOMAIN}"
    RAND_QTY=$((RANDOM % 4 + 1))
    RAND_PRICE="$((RANDOM % 1200 + 25)).$((RANDOM % 90 + 10))"

    JSON_PAYLOAD=$(cat <<EOF
{
  "item": "$RAND_ITEM",
  "email": "$RAND_EMAIL",
  "quantity": $RAND_QTY,
  "price": $RAND_PRICE
}
EOF
    )

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/orders" \
      -H "Content-Type: application/json" \
      -d "$JSON_PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" == "201" ]; then
        ORDER_ID=$(echo "$BODY" | grep -o '"order_id":"[^"]*' | cut -d'"' -f4)
        echo -e "  [${i}/${TOTAL_ORDERS}] ${GREEN}✔ Encolado en 'orders_queue'${NC} -> ${MAGENTA}${ORDER_ID:-ORD-OK}${NC} | ${CYAN}${RAND_ITEM}${NC} (x${RAND_QTY}) para ${YELLOW}${RAND_EMAIL}${NC} (\$${RAND_PRICE})"
        ((SUCCESS_COUNT++))
    else
        echo -e "  [${i}/${TOTAL_ORDERS}] ${RED}❌ Error HTTP ${HTTP_CODE}${NC}"
    fi
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}  ¡${SUCCESS_COUNT}/${TOTAL_ORDERS} Pedidos ingresados al pipeline con éxito! (${ELAPSED}s)${NC}"
echo -e "${GREEN}======================================================${NC}\n"
echo -e "👀 Monitorea los microservicios en vivo:"
echo -e "   Paso 1 (Cobro/Stock)  : ${CYAN}docker compose logs -f processor${NC}"
echo -e "   Paso 2 (Factura/Email): ${CYAN}docker compose logs -f notifier${NC}"
echo -e "   Todo el pipeline      : ${CYAN}docker compose logs -f processor notifier${NC}\n"
echo -e "⚡ Prueba el escalado horizontal independiente:"
echo -e "   ${CYAN}docker compose up --scale processor=3 --scale notifier=3 -d${NC}\n"
echo -e "🌐 O monitorea ambas colas ('orders_queue' y 'notifications_queue') en:"
echo -e "   ${CYAN}http://localhost:15672${NC} (Usuario: guest | Contraseña: guest)\n"
