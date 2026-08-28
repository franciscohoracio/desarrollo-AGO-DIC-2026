import os
import json
import time
import sys
from datetime import datetime
import pika

# Configuración de variables de entorno
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

INPUT_QUEUE = "orders_queue"
OUTPUT_QUEUE = "notifications_queue"


def connect_with_retry(max_retries=15, delay=3):
    """
    Intenta conectar a RabbitMQ con reintentos para asegurar resiliencia
    mientras el broker termina de inicializar.
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[PROCESSOR] Conectando a RabbitMQ en '{RABBITMQ_HOST}:{RABBITMQ_PORT}' (Intento {attempt}/{max_retries})...")
            connection = pika.BlockingConnection(parameters)
            print("[PROCESSOR] ✅ ¡Conexión establecida exitosamente con RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError as err:
            print(f"[PROCESSOR] ⏳ RabbitMQ no está listo aún ({err}). Reintentando en {delay}s...")
            time.sleep(delay)

    print("[PROCESSOR ERROR] ❌ No se pudo conectar a RabbitMQ después de varios intentos. Saliendo.")
    sys.exit(1)


def process_order(ch, method, properties, body):
    """
    Callback: Consume de orders_queue, valida stock/pago (5s) y transfiere a notifications_queue.
    """
    try:
        data = json.loads(body.decode("utf-8"))
        order_id = data.get("order_id", "DESCONOCIDO")
        email = data.get("email", "sin_correo")
        item = data.get("item", "articulo")
        qty = data.get("quantity", 1)
        price = data.get("price", 0.0)

        print("\n" + "=" * 55)
        print(f"⚙️  [PROCESSOR] Recibido pedido: {order_id}")
        print(f"   🛒 Artículo : {item} (x{qty})")
        print(f"   💰 Importe  : ${price}")
        print(f"   ⏳ [Paso 1/2] Validando stock y procesando cobro bancario...")

        # Simulación de tarea pesada de validación y pago (5 segundos)
        time.sleep(5)

        # Actualizar estado y timestamp en el payload del pedido
        data["status"] = "PROCESSED"
        data["processed_at"] = datetime.utcnow().isoformat()

        # Publicar el pedido procesado hacia la cola de notificaciones
        ch.basic_publish(
            exchange="",
            routing_key=OUTPUT_QUEUE,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
                content_type="application/json"
            )
        )

        print(f"   ✅ [ÉXITO] Cobro aprobado y stock reservado para {order_id}")
        print(f"   🚀 Pedido derivado a la cola '{OUTPUT_QUEUE}' para notificación")
        print("=" * 55 + "\n")

        # Confirmación (ACK) para remover de orders_queue
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[PROCESSOR ERROR] ❌ Error al procesar pedido: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    connection = connect_with_retry()
    channel = connection.channel()

    # Asegurar que ambas colas existan y sean durables
    channel.queue_declare(queue=INPUT_QUEUE, durable=True)
    channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

    # Fair Dispatch (1 mensaje a la vez por réplica)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=INPUT_QUEUE,
        on_message_callback=process_order
    )

    print(f"\n🚀 [PROCESSOR] Escuchando en '{INPUT_QUEUE}' y publicando en '{OUTPUT_QUEUE}'.")
    print("📌 Para salir presiona CTRL+C o detén el contenedor.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[PROCESSOR] Deteniendo procesador de forma segura...")
        channel.stop_consuming()
        connection.close()
        print("[PROCESSOR] Conexión cerrada. ¡Adiós!")


if __name__ == "__main__":
    main()
