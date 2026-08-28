# 🐳 Práctica 2.2: Contenerización y Microservicios con Docker y RabbitMQ

> **Materia:** Desarrollo de Proyectos de Software  
> **Institución:** UAdeC — Facultad de Sistemas  
> **Nivel:** Principiante / Intermedio  

---

## 🎯 Objetivo de la Práctica

Aprender los fundamentos de la contenerización y el desacoplamiento mediante **Pipelines Asíncronos de Microservicios** desarrollando un **Sistema de Pedidos, Cobro y Notificaciones** compuesto por:

1. **Productor (`orders_api`):** API REST en Python (FastAPI) que recibe pedidos de clientes y los deposita en la primera cola (`orders_queue`) en `<5ms`.
2. **Message Broker (`rabbitmq`):** Broker de mensajería AMQP que gestiona dos colas desacopladas y persistentes: `orders_queue` y `notifications_queue`.
3. **Procesador de Pedidos (`processor` - Paso 1):** Servicio en segundo plano que consume de `orders_queue`, simula la validación de inventario y cobro bancario (5s), actualiza el estado a `PROCESSED` y deposita el pedido en `notifications_queue`.
4. **Notificador de Pedidos (`notifier` - Paso 2):** Servicio en segundo plano que consume de `notifications_queue`, simula la generación de la factura electrónica y el envío de correo de confirmación (5s), finalizando con la confirmación `ACK`.
5. **Orquestación (`docker-compose`):** Gestión declarativa de todo el pipeline en una red virtual privada y con almacenamiento persistente.

---

## 🏗️ Arquitectura del Pipeline de Microservicios

```text
┌────────────────┐      HTTP POST       ┌────────────────────────┐
│  Cliente Web / ├─────────────────────►│  Orders API (Producer) │
│  cURL / Script │◄─────────────────────┤       (FastAPI)        │
└────────────────┘    201 Created       └───────────┬────────────┘
                        (en 5ms)                    │
                                                    │ AMQP (orders_queue)
                                                    ▼
                                        ┌────────────────────────┐
                                        │    RabbitMQ Broker     │
                                        │  [ Cola: orders_queue ]│
                                        └───────────┬────────────┘
                                                    │
                                                    │ AMQP (Fair Dispatch)
                                                    ▼
                                        ┌────────────────────────┐
                                        │ Order Processor Worker │
                                        │   (Paso 1: Cobro/Stock)│
                                        └───────────┬────────────┘
                                                    │
                                                    │ AMQP (notifications_queue)
                                                    ▼
                                        ┌────────────────────────┐
                                        │    RabbitMQ Broker     │
                                        │[notifications_queue]   │
                                        └───────────┬────────────┘
                                                    │
                                                    │ AMQP (Fair Dispatch)
                                                    ▼
                                        ┌────────────────────────┐
                                        │  Notification Worker   │
                                        │  (Paso 2: Email/Fact)  │
                                        └────────────────────────┘
```

---

## 📂 Estructura de Archivos del Proyecto

```text
2.2_Practica_Docker_RabbitMQ/
├── docker-compose.yml          # Orquestación declarativa de los 4 servicios
├── .dockerignore               # Archivos excluidos del build en Docker
├── .env.example                # Variables de entorno de referencia
├── test_orders.sh              # Script interactivo de generación de pedidos aleatorios
├── README.md                   # Esta guía práctica
│
├── orders_api/                 # MICROSERVICIO PRODUCTOR
│   ├── Dockerfile              # Imagen Docker para la API
│   ├── main.py                 # API en FastAPI + Pika
│   ├── requirements.txt        # Dependencias (fastapi, uvicorn, pika, pydantic, email-validator)
│   └── .dockerignore
│
├── processor/                  # MICROSERVICIO CONSUMIDOR/PRODUCTOR (Paso 1)
│   ├── Dockerfile              # Imagen Docker para el Procesador
│   ├── processor.py            # Consume de orders_queue -> Procesa cobro -> Publica en notifications_queue
│   ├── requirements.txt        # Dependencias (pika)
│   └── .dockerignore
│
└── notifier/                   # MICROSERVICIO CONSUMIDOR FINAL (Paso 2)
    ├── Dockerfile              # Imagen Docker para el Notificador
    ├── notifier.py             # Consume de notifications_queue -> Emite factura/correo -> ACK
    ├── requirements.txt        # Dependencias (pika)
    └── .dockerignore
```

---

## 🚀 Requisitos Previos

* Tener instalado **Docker Desktop** (o Docker Engine + Docker Compose v2).
* Terminal / Consola (Bash, Zsh, PowerShell o WSL).

Para verificar que Docker está activo:
```bash
docker --version
docker compose version
```

---

## 🛠️ Guía Paso a Paso de Ejecución

### Paso 1: Ubicarse en la carpeta de la práctica
```bash
cd /Users/framos/Documents/MaterialesClase/Desarrollo/Practicas/2.2_Practica_Docker_RabbitMQ
```

### Paso 2: Construir y Levantar el Stack Completo
Ejecuta el siguiente comando para compilar las imágenes y encender todos los contenedores:
```bash
docker compose up --build -d
```

---

## 🧪 Cómo Probar el Sistema

### Opción A: Usando el script interactivo automatizado (Recomendado)
Abre una pestaña de terminal y ejecuta:
```bash
./test_orders.sh
```
El script te preguntará cuántos pedidos deseas generar y creará pedidos con datos aleatorios (artículos, correos, precios y cantidades).

### Opción B: Interfaz Interactiva de Swagger UI
1. Abre tu navegador web en: **[http://localhost:8000/docs](http://localhost:8000/docs)**
2. Despliega el endpoint `POST /orders`.
3. Haz clic en **"Try it out"**, edita el JSON y presiona **"Execute"**:
```json
{
  "item": "Laptop Gamer Ryzen 7",
  "email": "estudiante@uadec.mx",
  "quantity": 1,
  "price": 1200.00
}
```

---

## 📊 Inspección y Monitoreo en RabbitMQ Management UI

1. Ingresa a: **[http://localhost:15672](http://localhost:15672)**
2. Credenciales por defecto:
   * **Usuario:** `guest`
   * **Contraseña:** `guest`
3. Ve a la pestaña **"Queues"** y podrás observar en tiempo real ambas colas:
   * `orders_queue`: Mensajes entrantes desde la API esperando al `processor`.
   * `notifications_queue`: Mensajes procesados esperando al `notifier`.

---

## 🧠 Retos Didácticos para el Estudiante

### Reto 1: Escalado Horizontal de Microservicios 📈
Prueba escalar ambos workers para procesar decenas de pedidos simultáneos en paralelo:

```bash
docker compose up --scale processor=3 --scale notifier=3 -d
```
Luego envía 15 pedidos con `./test_orders.sh 15` y observa con `docker compose logs -f processor notifier` cómo RabbitMQ distribuye el trabajo en paralelo entre las réplicas.

### Reto 2: Prueba de Resiliencia ante Caídas en el Pipeline 🛡️
1. Apaga el microservicio notificador:
   ```bash
   docker compose stop notifier
   ```
2. Envía varios pedidos con `./test_orders.sh 5`.
3. Observa cómo el `processor` atiende los pedidos y los transfiere a `notifications_queue`.
4. Abre la consola de RabbitMQ (`http://localhost:15672/`): verás los mensajes acumulados de forma segura en `notifications_queue`.
5. Vuelve a encender el notificador:
   ```bash
   docker compose start notifier
   ```
6. El `notifier` consumirá y procesará inmediatamente todos los pedidos acumulados sin pérdida de información.

---

## 🛑 Detener y Limpiar el Entorno

Para detener todos los contenedores:
```bash
docker compose down
```

Para detener y borrar también los volúmenes de datos de RabbitMQ:
```bash
docker compose down -v
```

---

## 💡 Conceptos Clave Aprendidos en esta Práctica

* **Patrón Pipeline / Coreografía:** Descomposición de procesos de negocio complejos en etapas independientes unidas por colas de mensajería.
* **Aislamiento de Entornos:** Cada microservicio corre en su propio contenedor sin dependencias globales en el host.
* **Desacoplamiento Temporal:** La API responde en `<5ms` independientemente del tiempo que tarden las etapas posteriores.
* **Garantía At-Least-Once con ACK:** Ningún pedido se pierde si una etapa intermedia falla o se reinicia.
