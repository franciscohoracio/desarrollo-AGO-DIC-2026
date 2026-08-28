import os
import json
import time
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
import pika

app = FastAPI(
    title="Orders Service (Producer API)",
    description="Microservicio Productor: Recibe pedidos HTTP y los encola en RabbitMQ.",
    version="1.0.0"
)

# Configuración de variables de entorno (con valores por defecto)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "orders_queue"


class OrderRequest(BaseModel):
    item: str
    email: EmailStr
    quantity: int = 1
    price: float = 0.0


def get_rabbitmq_channel():
    """
    Establece conexión con RabbitMQ con reintentos para tolerar el tiempo de arranque.
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        connection_attempts=5,
        retry_delay=2
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    # Declara la cola como durable para que no se pierda al reiniciar RabbitMQ
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return connection, channel


@app.get("/", tags=["General"])
def read_root():
    return {
        "service": "Orders API (Producer)",
        "status": "online",
        "docs_url": "/docs",
        "rabbitmq_host": RABBITMQ_HOST,
        "queue": QUEUE_NAME
    }


@app.get("/health", tags=["General"])
def health_check():
    try:
        connection, channel = get_rabbitmq_channel()
        connection.close()
        return {"status": "healthy", "broker": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo conectar a RabbitMQ: {str(e)}"
        )


@app.post("/orders", status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def create_order(order_data: OrderRequest):
    """
    Recibe un pedido, genera un identificador único y lo publica en RabbitMQ.
    """
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    timestamp = datetime.utcnow().isoformat()

    order_payload = {
        "order_id": order_id,
        "item": order_data.item,
        "email": order_data.email,
        "quantity": order_data.quantity,
        "price": order_data.price,
        "created_at": timestamp,
        "status": "QUEUED"
    }

    try:
        connection, channel = get_rabbitmq_channel()

        # Publicación del mensaje con persistencia (delivery_mode=2)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(order_payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente en disco
                content_type="application/json"
            )
        )
        connection.close()

        print(f"[PRODUCER] ✅ Pedido {order_id} publicado en la cola '{QUEUE_NAME}'")

        return {
            "message": "Pedido recibido y encolado para procesamiento",
            "order": order_payload
        }
    except Exception as e:
        print(f"[PRODUCER ERROR] ❌ Error al publicar en RabbitMQ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comunicar con RabbitMQ: {str(e)}"
        )
