# 🌐 Práctica 2.3: Diseño de Interfaces de Comunicación y APIs
## (RESTful, Swagger, JWT, GraphQL, gRPC, WebSockets, SSE y Webhooks)

> **Materia:** Desarrollo de Proyectos de Software  
> **Institución:** UAdeC — Facultad de Sistemas  
> **Nivel:** Principiante / Intermedio  
> **Eje Temático:** Unidad 2 · Arquitectura de Software Contemporánea y Ecosistema Cloud-Native  

---

## 🎯 Objetivo de la Práctica

Comprender, implementar y comparar en vivo los principales **estilos y protocolos de comunicación entre aplicaciones** del desarrollo de software moderno a través de un ecosistema compuesto por 4 microservicios contenerizados:

1. **RESTful API Service (`rest_service` - Puerto 8001):**
   * Buenas prácticas de diseño de URIs con sustantivos y verbos HTTP (`GET`, `POST`, `DELETE`).
   * Códigos de estado HTTP correctos (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`).
   * Versionado de APIs en la URL (`/v1` vs `/v2`) para evolucionar sin romper clientes existentes.
   * Documentación viva e interactiva con **OpenAPI y Swagger UI**.
   * Seguridad basada en **Tokens JWT (JSON Web Tokens)** con validación *Stateless* y control de acceso por roles (RBAC).

2. **GraphQL Service (`graphql_service` - Puerto 8002):**
   * Eliminación del **Over-fetching** (descarga innecesaria de datos en dispositivos móviles).
   * Eliminación del **Under-fetching** (múltiples llamadas secuenciales para armar una pantalla).
   * Esquema fuertemente tipado (*Types, Queries, Mutations, Resolvers*) y explorador interactivo **GraphiQL**.

3. **gRPC High-Performance Service (`grpc_service` - Puerto 50051):**
   * Comunicación binaria ultrarrápida Backend-to-Backend mediante **Protocol Buffers (`.proto`)** sobre **HTTP/2**.
   * Comparativa de rendimiento frente a JSON/HTTP 1.1 (latencia en microsegundos).
   * Patrones de comunicación: **RPC Unario** y **RPC Server Streaming** (flujo continuo de telemetría).

4. **Real-Time & Webhooks Service (`realtime_service` - Puerto 8003):**
   * **WebSockets:** Canal bidireccional permanente (*full-duplex*) para chat y colaboración en vivo.
   * **Server-Sent Events (SSE):** Flujo unidireccional servidor-a-cliente para generación de texto progresiva (simulando ChatGPT / LLMs).
   * **Webhooks:** Notificaciones asíncronas basadas en eventos (*"No me llames, yo te aviso"*).
   * **Dashboard Web Interactivo:** Interfaz visual servida en el navegador para experimentar todos los flujos en tiempo real.

---

## 🏗️ Arquitectura del Ecosistema de Comunicación

```text
                                 ┌──────────────────────────────────────────────────┐
                                 │              CLIENTES / FRONTEND                 │
                                 │  (Navegador Web / Apps Móviles / CLI / Postman)  │
                                 └─────────┬──────────────┬──────────────┬──────────┘
                                           │              │              │
                    HTTP/1.1 (JSON)        │              │ GraphQL      │ WebSocket / SSE
                 ┌─────────────────────────┘              │ POST         │ (Tiempo Real)
                 ▼                                        ▼              ▼
     ┌───────────────────────┐               ┌───────────────────────┐ ┌───────────────────────┐
     │   REST API Service    │               │    GraphQL Service    │ │   Real-Time Service   │
     │       (Puerto 8001)   │               │       (Puerto 8002)   │ │       (Puerto 8003)   │
     ├───────────────────────┤               ├───────────────────────┤ ├───────────────────────┤
     │ • Swagger UI (/docs)  │               │ • GraphiQL (/graphql) │ │ • WebSockets (/ws)    │
     │ • JWT Auth (/auth)    │               │ • Menú a la carta     │ │ • SSE AI Stream       │
     │ • Versionado v1 vs v2 │               │ • Zero Over-fetching  │ │ • Webhooks de Pago    │
     └───────────┬───────────┘               └───────────┬───────────┘ └───────────┬───────────┘
                 │                                       │                         │
                 └───────────────────────────────┬───────┴─────────────────────────┘
                                                 │
                                                 │ gRPC (HTTP/2 + Protocol Buffers)
                                                 │ Binario Ultrarrápido (<1ms)
                                                 ▼
                                     ┌───────────────────────┐
                                     │  gRPC Analytics Core  │
                                     │      (Puerto 50051)   │
                                     ├───────────────────────┤
                                     │ • RPC Unario          │
                                     │ • Server Streaming    │
                                     │ • analytics.proto     │
                                     └───────────────────────┘
```

---

## 📊 Guía Comparativa de Estilos de Comunicación

| Tecnología | Analogía Cotidiana | Formato de Datos | ¿Para qué sirve principalmente? | ¿Cuándo elegirla? |
|---|---|---|---|---|
| **REST** | El restaurante con menú fijo | JSON / Texto | APIs públicas y páginas web tradicionales | Tu opción estándar para empezar cualquier proyecto. |
| **GraphQL** | Menú a la carta (Buffet) | JSON estructurado | Pantallas móviles complejas | Cuando quieras evitar transferir datos de más o de menos. |
| **gRPC** | Bólido de carreras (Telégrafo) | Protobuf (Binario) | Comunicación interna entre microservicios | Microservicios backend donde la latencia mínima es crítica. |
| **WebSockets** | Llamada telefónica abierta | Texto / JSON / Binario | Chats interactivos y colaboración multiusuario | Juegos online, WhatsApp Web, Figma o editores compartidos. |
| **Server-Sent Events (SSE)** | Estación de radio en vivo | Flujo `text/event-stream` | El servidor empuja actualizaciones continuas | Respuestas de Inteligencia Artificial (ChatGPT), cotizaciones o alertas. |
| **Webhooks** | Aviso de paquetería | JSON (HTTP POST) | Servidores avisándose entre sí al ocurrir eventos | Pagos con tarjeta (Stripe, PayPal), alertas de GitHub o CI/CD. |

---

## 📂 Estructura de Archivos del Proyecto

```text
2.3_Practica_Interfaces_y_APIs/
├── docker-compose.yml             # Orquestación de los 4 microservicios en una red privada
├── test_apis.sh                   # Script interactivo de pruebas con menú a color
├── README.md                      # Esta guía práctica detallada
├── diagrama_practica.excalidraw   # Diagrama visual de arquitectura (Excalidraw)
├── diagrama_practica.excalidraw.md# Wrapper del diagrama para Obsidian
│
├── rest_service/                  # MÓDULO 1: RESTful API + OpenAPI (Swagger) + JWT + Versionado
│   ├── Dockerfile                 # Imagen Docker para REST API
│   ├── requirements.txt           # Dependencias (fastapi, uvicorn, pyjwt, pydantic)
│   ├── main.py                    # Endpoints /auth/login, /v1/students, /v2/students, Bearer Auth
│   └── .dockerignore
│
├── graphql_service/               # MÓDULO 2: GraphQL Service & Playground
│   ├── Dockerfile                 # Imagen Docker para GraphQL
│   ├── requirements.txt           # Dependencias (strawberry-graphql, fastapi, uvicorn)
│   ├── main.py                    # Tipos, Queries, Mutations, Resolvers y GraphiQL Playground
│   └── .dockerignore
│
├── grpc_service/                  # MÓDULO 3: gRPC & Protocol Buffers Backend-to-Backend
│   ├── Dockerfile                 # Imagen Docker con compilación de .proto
│   ├── requirements.txt           # Dependencias (grpcio, grpcio-tools, protobuf)
│   ├── server.py                  # Servidor gRPC (RPC Unario y Server Streaming)
│   ├── client.py                  # Cliente gRPC de prueba y benchmark de latencia
│   ├── analytics_pb2.py           # Clases generadas por protoc
│   ├── analytics_pb2_grpc.py      # Stubs de cliente y servidor generados
│   ├── protos/
│   │   └── analytics.proto        # Contrato binario .proto con tags numéricos (1, 2, 3...)
│   └── .dockerignore
│
└── realtime_service/              # MÓDULO 4: Tiempo Real (WebSockets, SSE y Webhooks)
    ├── Dockerfile                 # Imagen Docker para Tiempo Real
    ├── requirements.txt           # Dependencias (fastapi, uvicorn, websockets)
    ├── main.py                    # Handlers de WebSockets, SSE generator y Webhook receiver
    ├── static/
    │   └── index.html             # Dashboard Web interactivo en tiempo real
    └── .dockerignore
```

---

## 🚀 Requisitos Previos

* Tener instalado **Docker Desktop** (o Docker Engine + Docker Compose v2).
* Terminal / Consola (Bash, Zsh o WSL).
* Un navegador web moderno (Chrome, Firefox, Safari o Edge).

Para verificar que Docker está activo:
```bash
docker --version
docker compose version
```

---

## 🛠️ Guía Paso a Paso de Ejecución

### Paso 1: Ubicarse en la carpeta de la práctica
```bash
cd /Users/framos/DevOps/desarrollo-AGO-DIC-2026/2.3_Practica_Interfaces_y_APIs
```

### Paso 2: Construir y Levantar los 4 Microservicios
Ejecuta el siguiente comando para compilar las imágenes y levantar el stack completo:
```bash
docker compose up --build -d
```

Verifica que los 4 contenedores estén en estado `Up`:
```bash
docker compose ps
```

---

## 🧪 Cómo Probar el Sistema

### Opción A: Usar el Script Interactivo Automatizado (Recomendado)
Abre tu terminal y ejecuta:
```bash
./test_apis.sh
```

El script desplegará un menú interactivo con opciones numeradas para probar cada protocolo:
* **[1]** Probar REST API, Versionado y Seguridad JWT.
* **[2]** Probar GraphQL (Comparativa Over-fetching vs Consulta a la carta).
* **[3]** Probar gRPC & Protobuf (Llamada Unaria y Server Streaming).
* **[4]** Probar Tiempo Real (WebSockets, SSE y Webhooks).
* **[5]** Ejecutar Benchmark Comparativo de Rendimiento (REST vs GraphQL vs gRPC).
* **[6]** Mostrar y abrir enlaces directos en el navegador.

---

### Opción B: Explorar REST API y Seguridad JWT con Swagger UI

1. Abre en tu navegador: **[http://localhost:8001/docs](http://localhost:8001/docs)**
2. Observa cómo **Swagger UI** genera la documentación viva de todos los endpoints.
3. **Paso de Autenticación (Obtener la Pulsera VIP):**
   * Despliega `POST /auth/login`, haz clic en **"Try it out"** y usa:
     ```json
     {
       "email": "docente@uadec.mx",
       "password": "password123"
     }
     ```
   * Copia el valor de `access_token` generado.
4. **Autorizar en Swagger:**
   * Haz clic en el botón verde **"Authorize"** 🔒 en la parte superior derecha de la página.
   * En el campo de texto, pega tu token y haz clic en **"Authorize"**.
5. **Probar Endpoint Protegido:**
   * Despliega `POST /v2/students` y registra un alumno con éxito (`HTTP 201 Created`).
   * Prueba cerrar la sesión (cerrar el candado) e intentar registrar otro alumno: recibirás un `HTTP 401 Unauthorized`.

---

### Opción C: Consultas Flexibles con GraphiQL Playground

1. Abre en tu navegador: **[http://localhost:8002/graphql](http://localhost:8002/graphql)**
2. **Prueba 1 (Consulta Ultra Ligera — Cero Over-fetching):**
   Pega esta consulta en el panel izquierdo y presiona el botón **Play (▶)**:
   ```graphql
   query {
     student(matricula: "12345") {
       nombre
       promedio
     }
   }
   ```
   *Nota que NO se descargaron CURP, dirección, teléfonos ni historiales médicos.*

3. **Prueba 2 (Consulta Anidada Relacional — Cero Under-fetching):**
   ```graphql
   query {
     student(matricula: "12345") {
       nombre
       carrera
       materias {
         codigo
         nombre
         profesor
         calificacion
       }
     }
   }
   ```
   *En 1 sola petición obtuviste al estudiante, sus materias y los profesores asignados.*

4. **Prueba 3 (Mutación para Inscribir Materia):**
   ```graphql
   mutation {
     enrollStudent(matricula: "12345", codigoMateria: "BD-2026", calificacion: 98.5) {
       nombre
       materias {
         nombre
         calificacion
       }
     }
   }
   ```

---

### Opción D: Dashboard en Tiempo Real (WebSockets, SSE y Webhooks)

1. Abre en tu navegador: **[http://localhost:8003](http://localhost:8003)**
2. **Probar WebSockets:**
   * Abre **dos pestañas** de tu navegador en `http://localhost:8003`.
   * En una pestaña escribe con el nombre *Carlos* y en la otra con *Ana*.
   * Envía mensajes y observa cómo aparecen instantáneamente en ambas pantallas sin recargar la página.
3. **Probar Server-Sent Events (SSE):**
   * En la columna central, selecciona un tema y haz clic en **"Iniciar Stream SSE"**.
   * Observa cómo el servidor envía palabras en tiempo real con una barra de progreso progresiva.
4. **Probar Webhooks:**
   * Haz clic en **"Disparar Webhook de Pago Exitoso"**.
   * Observa cómo el webhook notifica al servidor (`POST /webhooks/tuition-payment`) y este lo retransmite al instante al canal de WebSockets de todos los usuarios conectados.

---

### Opción E: Pruebas de gRPC por Consola (Microsegundos y Streaming)

Desde tu terminal, puedes ejecutar el cliente de gRPC directamente dentro del contenedor:

1. **Llamada Unaria Ultrarrápida:**
   ```bash
   docker compose exec grpc_service python client.py --unary --matricula 12345
   ```
2. **Server Streaming en Vivo:**
   ```bash
   docker compose exec grpc_service python client.py --stream --total 5
   ```
3. **Benchmark de Rendimiento:**
   ```bash
   docker compose exec grpc_service python client.py --benchmark --requests 200
   ```

---

## 🧠 Retos Didácticos para el Estudiante

### Reto 1: Alterar y Romper la Firma de un JWT 🛡️
1. Inicia sesión en Swagger (`http://localhost:8001/docs`) y copia tu token JWT.
2. Abre [jwt.io](https://jwt.io) y pega tu token para inspeccionar sus 3 partes: **Header** (rojo), **Payload** (morado) y **Signature** (azul).
3. Intenta cambiar tu rol de `"alumno"` a `"admin"` editando el texto del token manualmente y envíalo en la cabecera `Authorization: Bearer <token_alterado>`.
4. Observa cómo el servidor rechaza inmediatamente la petición con `HTTP 401 Token Inválido` debido a que el sello matemático de la firma ya no coincide.

### Reto 2: Crear una Consulta GraphQL para Smartwatch ⌚
Imagina que estás programando una aplicación para un reloj inteligente con pantalla de 1 pulgada:
* Diseña una consulta en **GraphiQL** (`http://localhost:8002/graphql`) que traiga a todos los alumnos (`students`) pero pidiendo **únicamente** su `matricula` y su `promedio`.
* Comprueba que la respuesta sea un JSON minúsculo que ahorra el 90% de batería y datos móviles.

### Reto 3: Modificar el Contrato Protobuf (`.proto`) ⚡
1. Abre el archivo `grpc_service/protos/analytics.proto`.
2. Agrega un nuevo campo al mensaje `StudentMetricsResponse`:
   ```protobuf
   string mencion_honorifica = 8;
   ```
3. Recompila el servicio ejecutando `docker compose up --build -d grpc_service`.
4. Modifica `grpc_service/server.py` para asignar el valor y verifica con `python client.py --unary`.

---

## 🛑 Detener y Limpiar el Entorno

Para detener todos los contenedores de la práctica:
```bash
docker compose down
```

Para detener y eliminar imágenes y redes asociadas:
```bash
docker compose down --rmi local
```

---

## 💡 Conceptos Clave Aprendidos en esta Práctica

* **El Mesero Digital (API):** Conecta aplicaciones permitiendo solicitar y enviar datos usando verbos estandarizados y rutas basadas en recursos.
* **Documentación con Swagger:** Crea el menú oficial de la API de forma automática directamente desde el código fuente.
* **Pases Temporales (JWT):** Pulseras digitales selladas con criptografía que permiten autenticación *Stateless* ultrarrápida sin sobrecargar la base de datos.
* **GraphQL y el Menú a la Carta:** Permite al frontend pedir exactamente la forma de los datos que necesita, eliminando el desperdicio de red.
* **gRPC y Protocol Buffers:** El estándar de la industria para microservicios internos que requieren máxima velocidad y contratos binarios estrictos.
* **Tiempo Real Adaptativo:** WebSockets para colaboración bidireccional continua, Server-Sent Events para streams unidireccionales de IA, y Webhooks para comunicación asíncrona entre plataformas.
