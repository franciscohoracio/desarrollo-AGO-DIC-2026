import os
import json
import time
import sys
import pika

# Configuración leída de variables de entorno
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

QUEUE_NAME = "notifications_queue"


def connect_with_retry(max_retries=15, delay=3):
    """
    Intenta conectar a RabbitMQ con reintentos para asegurar resiliencia
    mientras el broker termina de iniciar.
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
            print(f"[NOTIFIER] Conectando a RabbitMQ en '{RABBITMQ_HOST}:{RABBITMQ_PORT}' (Intento {attempt}/{max_retries})...")
            connection = pika.BlockingConnection(parameters)
            print("[NOTIFIER] ✅ ¡Conexión establecida exitosamente con RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError as err:
            print(f"[NOTIFIER] ⏳ RabbitMQ no está listo aún ({err}). Reintentando en {delay}s...")
            time.sleep(delay)

    print("[NOTIFIER ERROR] ❌ No se pudo conectar a RabbitMQ después de varios intentos. Saliendo.")
    sys.exit(1)


def process_notification(ch, method, properties, body):
    """
    Callback: Consume de notifications_queue y simula emisión de factura y envío de correo (5s).
    """
    try:
        data = json.loads(body.decode("utf-8"))
        order_id = data.get("order_id", "DESCONOCIDO")
        email = data.get("email", "sin_correo")
        item = data.get("item", "articulo")
        qty = data.get("quantity", 1)
        price = data.get("price", 0.0)

        print("\n" + "=" * 55)
        print(f"📧 [NOTIFIER] Recibido pedido para notificación: {order_id}")
        print(f"   👤 Destinatario : {email}")
        print(f"   🛒 Artículo     : {item} (x{qty}) - ${price}")
        print(f"   ⏳ [Paso 2/2] Generando factura PDF y enviando correo de confirmación...")

        # Simulación de tarea pesada de notificación / envío de email (5 segundos)
        time.sleep(5)

        print(f"   ✅ [ÉXITO] Factura y correo de confirmación enviados a {email}")
        print(f"   🎉 ¡Ciclo completo finalizado para el pedido {order_id}!")
        print("=" * 55 + "\n")

        # Confirmación manual (ACK) a RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[NOTIFIER ERROR] ❌ Error procesando notificación: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    connection = connect_with_retry()
    channel = connection.channel()

    # Asegura que la cola exista y sea durable
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Fair Dispatch (1 mensaje a la vez por réplica)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=process_notification
    )

    print(f"\n🚀 [NOTIFIER] Esperando pedidos en la cola '{QUEUE_NAME}'.")
    print("📌 Para salir presiona CTRL+C o detén el contenedor.\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[NOTIFIER] Deteniendo notificador de forma segura...")
        channel.stop_consuming()
        connection.close()
        print("[NOTIFIER] Conexión cerrada. ¡Adiós!")


if __name__ == "__main__":
    main()
