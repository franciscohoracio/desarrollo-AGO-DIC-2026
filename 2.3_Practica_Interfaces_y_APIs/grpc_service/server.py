"""
=============================================================================
⚡ MICROSERVICIO gRPC: Comunicación Binaria Backend-to-Backend de Alta Escala
=============================================================================
Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
Tema 2.3: Interfaces de Comunicación y APIs

Conceptos Clave Demostrados:
1. Protocol Buffers (.proto): Contrato binario estricto sin sobrecarga de texto JSON.
2. Latencia Ultra-Baja: Ideal para microservicios internos que procesan miles de req/s.
3. RPC Unario: Petición y respuesta directa en microsegundos.
4. RPC Server Streaming: Servidor enviando flujo continuo de datos sin cerrar conexión.
=============================================================================
"""

import time
import random
from concurrent import futures
from datetime import datetime
import grpc

# Importar stubs generados por el compilador protoc
import analytics_pb2
import analytics_pb2_grpc

# Base de datos simulada de analítica académica
STUDENTS_METRICS_DATA = {
    12345: {
        "nombre": "Carlos Gómez",
        "promedio": 94.5,
        "aprobadas": 38,
        "reprobadas": 0,
        "nivel": "EXCELENCIA_ACADEMICA"
    },
    67890: {
        "nombre": "Ana Morales",
        "promedio": 98.2,
        "aprobadas": 26,
        "reprobadas": 0,
        "nivel": "ALTO_RENDIMIENTO"
    },
    11223: {
        "nombre": "Luis Hernández",
        "promedio": 83.0,
        "aprobadas": 45,
        "reprobadas": 2,
        "nivel": "REGULAR"
    }
}


class AnalyticsServiceServicer(analytics_pb2_grpc.AnalyticsServiceServicer):
    """
    Implementación del servicio gRPC definido en analytics.proto
    """

    def GetStudentMetrics(self, request, context):
        """
        1. RPC UNARIO:
        Recibe matrícula en formato binario, procesa en memoria y retorna métricas.
        """
        start_ns = time.perf_counter_ns()
        matricula = request.matricula

        # Simular procesamiento en microsegundos
        student_data = STUDENTS_METRICS_DATA.get(matricula, {
            "nombre": f"Estudiante Generado #{matricula}",
            "promedio": 88.5,
            "aprobadas": 30,
            "reprobadas": 1,
            "nivel": "BUENO"
        })

        elapsed_us = (time.perf_counter_ns() - start_ns) // 1000

        print(f"[gRPC UNARY] ⚡ Consulta rápida de matrícula: {matricula} -> Retornado en {elapsed_us} µs")

        return analytics_pb2.StudentMetricsResponse(
            matricula=matricula,
            nombre=student_data["nombre"],
            promedio=student_data["promedio"],
            materias_aprobadas=student_data["aprobadas"],
            materias_reprobadas=student_data["reprobadas"],
            nivel_desempeno=student_data["nivel"],
            latencia_calculo_microsegundos=elapsed_us
        )

    def StreamCampusTelemetry(self, request, context):
        """
        2. RPC SERVER STREAMING:
        Mantiene un canal abierto sobre HTTP/2 y emite un flujo continuo de telemetría.
        """
        campus = request.campus_id or "UAdeC-Saltillo-Main"
        total = request.total_eventos if request.total_eventos > 0 else 5
        intervalo_s = max(0.2, (request.intervalo_ms or 1000) / 1000.0)

        print(f"\n[gRPC STREAMING] 📡 Iniciando Server Streaming de {total} eventos para '{campus}'...")

        sensors = [
            ("CPU_CLUSTER_LOAD", "%", (15.0, 75.0)),
            ("MEMORY_USAGE", "GB", (8.0, 32.0)),
            ("CAMPUS_WIFI_ACTIVE_CLIENTS", "usuarios", (1200.0, 3500.0)),
            ("API_GATEWAY_THROUGHPUT", "req/s", (450.0, 2800.0)),
            ("LATENCY_P99", "ms", (1.2, 8.5))
        ]

        for i in range(1, total + 1):
            sensor_name, unit, (val_min, val_max) = random.choice(sensors)
            val = round(random.uniform(val_min, val_max), 2)
            status_text = "NORMAL" if val < (val_max * 0.85) else "ELEVADO"
            
            event = analytics_pb2.TelemetryEvent(
                sequence_id=i,
                sensor=f"[{campus}] {sensor_name}",
                valor=val,
                unidad=unit,
                estado=status_text,
                timestamp=datetime.utcnow().isoformat()
            )

            print(f"   📤 Transmitiendo frame #{i}/{total}: {sensor_name} = {val} {unit}")
            yield event
            time.sleep(intervalo_s)

        print(f"[gRPC STREAMING] ✅ Stream completado exitosamente.\n")


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analytics_pb2_grpc.add_AnalyticsServiceServicer_to_server(
        AnalyticsServiceServicer(), server
    )
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print("=" * 60)
    print(f"🚀 [gRPC SERVICE] Servidor gRPC activo y escuchando en el puerto {port}")
    print("📌 Protocolo: HTTP/2 + Protocol Buffers (Binario)")
    print("=" * 60)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
