"""
=============================================================================
🔴 MICROSERVICIO DE TIEMPO REAL: WebSockets, Server-Sent Events y Webhooks
=============================================================================
Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
Tema 2.3: Interfaces de Comunicación y APIs

Conceptos Clave Demostrados:
1. WebSockets: Canal permanente bidireccional full-duplex (chat/colaboración en vivo).
2. Server-Sent Events (SSE): Flujo continuo unidireccional servidor -> cliente (tipo ChatGPT).
3. Webhooks: Notificaciones basadas en eventos asíncronos ("No me llames, yo te aviso").
4. Dashboard Web interactivo en tiempo real servido en la raíz (/).
=============================================================================
"""

import os
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Header
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="📡 Campus Real-Time Service",
    description="Microservicio para comunicación en tiempo real con WebSockets, SSE y Webhooks.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# GESTOR DE CONEXIONES WEBSOCKETS (CANAL BIDIRECCIONAL PERMANENTE)
# =============================================================================
class ConnectionManager:
    """
    Administra la lista de sockets activos y distribuye mensajes a todos los clientes.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WEBSOCKET] 🟢 Nuevo cliente conectado. Total activos: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WEBSOCKET] 🔴 Cliente desconectado. Total activos: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """
        Envía un mensaje JSON a todas las conexiones abiertas en simultáneo.
        """
        payload = json.dumps(data)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                print(f"[WEBSOCKET ERROR] Fallo al enviar a cliente: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# =============================================================================
# MODELO PYDANTIC PARA WEBHOOKS
# =============================================================================
class WebhookPaymentPayload(BaseModel):
    transaccion_id: str = Field(..., example="TXN-9988234")
    matricula: str = Field(..., example="12345")
    alumno: str = Field(..., example="Carlos Gómez")
    monto: float = Field(..., example=3450.00)
    concepto: str = Field(..., example="Inscripción Semestre Ago-Dic 2026")
    banco_emisor: str = Field("BBVA / Stripe", example="BBVA")

# =============================================================================
# 1. ENDPOINT WEBSOCKET: CHAT Y NOTIFICACIONES EN VIVO
# =============================================================================
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    Canal de comunicación permanente bidireccional.
    Tanto el cliente como el servidor pueden enviar mensajes en cualquier momento sin recargar la página.
    """
    await manager.connect(websocket)
    try:
        # Enviar mensaje de bienvenida al cliente recién conectado
        await websocket.send_text(json.dumps({
            "tipo": "SISTEMA",
            "autor": "Servidor Campus",
            "mensaje": "¡Conectado al canal WebSocket en tiempo real!",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }))
        
        while True:
            # Esperar mensaje entrante del cliente
            raw_data = await websocket.receive_text()
            try:
                msg_data = json.loads(raw_data)
            except json.JSONDecodeError:
                msg_data = {"autor": "Invitado", "mensaje": raw_data}
                
            autor = msg_data.get("autor", "Anónimo")
            texto = msg_data.get("mensaje", "")
            
            print(f"[WEBSOCKET IN] Mensaje de {autor}: {texto}")
            
            # Difundir el mensaje a todos los usuarios conectados
            await manager.broadcast({
                "tipo": "CHAT",
                "autor": autor,
                "mensaje": texto,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "tipo": "SISTEMA",
            "autor": "Servidor Campus",
            "mensaje": "Un usuario ha salido del chat.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

# =============================================================================
# 2. ENDPOINT SERVER-SENT EVENTS (SSE): STREAMING UNIDIRECCIONAL SERVIDOR -> CLIENTE
# =============================================================================
async def sse_event_generator(pregunta: str):
    """
    Generador asíncrono que simula la respuesta de un Modelo de IA / ChatGPT
    emitiendo tokens palabra por palabra a través del protocolo Server-Sent Events.
    """
    respuestas = {
        "rest": "REST es un estilo arquitectónico basado en recursos identificados por URLs y verbos HTTP estándar como GET, POST, PUT y DELETE. Es la opción predeterminada para la web pública.",
        "graphql": "GraphQL permite al cliente solicitar exactamente los campos necesarios en una sola llamada POST, resolviendo problemas de Over-fetching y Under-fetching.",
        "grpc": "gRPC utiliza Protocol Buffers y HTTP/2 para transmitir mensajes binarios ultrarrápidos entre servidores internos con latencia de microsegundos.",
        "default": f"Para responder a tu consulta sobre '{pregunta}': En el desarrollo moderno de software, la elección del protocolo de comunicación depende del caso de uso. Hacia clientes web y móviles usamos REST y GraphQL, mientras que internamente entre microservicios preferimos gRPC y colas de eventos."
    }
    
    clave = "default"
    for k in respuestas:
        if k in pregunta.lower():
            clave = k
            break
            
    texto_completo = respuestas[clave]
    palabras = texto_completo.split(" ")
    
    yield f"data: {json.dumps({'status': 'iniciando', 'total_palabras': len(palabras)})}\n\n"
    await asyncio.sleep(0.3)
    
    for idx, palabra in enumerate(palabras):
        evento = {
            "index": idx + 1,
            "palabra": palabra + " ",
            "progreso": round(((idx + 1) / len(palabras)) * 100, 1),
            "finalizado": (idx + 1 == len(palabras))
        }
        yield f"data: {json.dumps(evento)}\n\n"
        await asyncio.sleep(0.08)  # Simular tiempo de inferencia de IA


@app.get("/sse/ai-tutor", tags=["Tiempo Real"])
async def sse_ai_tutor(pregunta: str = "Explica los estilos de comunicación en APIs"):
    """
    📡 **Server-Sent Events (SSE)**:
    Transmite la respuesta de forma progresiva sin cerrar la conexión HTTP (Content-Type: text/event-stream).
    """
    return StreamingResponse(
        sse_event_generator(pregunta),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# =============================================================================
# 3. ENDPOINT WEBHOOK: AVISO DE EVENTO ASÍNCRONO ("NO ME LLAMES, YO TE AVISO")
# =============================================================================
@app.post("/webhooks/tuition-payment", status_code=status.HTTP_200_OK, tags=["Tiempo Real"])
async def receive_payment_webhook(
    payload: WebhookPaymentPayload,
    x_webhook_secret: str = Header(default="uadec-secret-token")
):
    """
    🔔 **Webhook Receptor**:
    Simula la notificación automática que un procesador de pagos externo (como Stripe o PayPal)
    envía a nuestro servidor cuando un alumno completa un pago.
    Al recibirlo, se retransmite inmediatamente por WebSockets a todos los navegadores abiertos.
    """
    print(f"\n[WEBHOOK RECIBIDO] 💰 Pago confirmado: ${payload.monto} MXN de {payload.alumno} ({payload.matricula})")
    
    # Notificar al instante a todos los clientes conectados al WebSocket
    await manager.broadcast({
        "tipo": "ALERTA_PAGO",
        "autor": "🏦 Sistema Bancario (Webhook)",
        "mensaje": f"¡Pago recibido con éxito! ${payload.monto:,.2f} MXN — Concepto: {payload.concepto} ({payload.alumno})",
        "datos": payload.model_dump(),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    return {
        "status": "received",
        "message": f"Webhook procesado y notificado a {len(manager.active_connections)} clientes activos en tiempo real.",
        "transaction_id": payload.transaccion_id
    }

# =============================================================================
# 4. DASHBOARD WEB INTERACTIVO EN VIVO
# =============================================================================
@app.get("/", response_class=HTMLResponse, tags=["General"])
async def get_dashboard():
    """
    Sirve el Dashboard Web interactivo para probar WebSockets, SSE y Webhooks visualmente.
    """
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Campus Real-Time Service activo. Visita /docs para API</h1>"

@app.get("/health", tags=["General"])
def health():
    return {
        "status": "healthy",
        "service": "realtime_api",
        "active_websockets": len(manager.active_connections)
    }
