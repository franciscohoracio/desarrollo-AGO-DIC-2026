"""
=============================================================================
💻 CLIENTE DE PRUEBA gRPC: Consumidor de RPC Unario y Streaming
=============================================================================
Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
Tema 2.3: Interfaces de Comunicación y APIs
=============================================================================
"""

import os
import sys
import time
import argparse
import grpc

import analytics_pb2
import analytics_pb2_grpc

GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")


def get_channel():
    target = f"{GRPC_HOST}:{GRPC_PORT}"
    return grpc.insecure_channel(target)


def test_unary(matricula: int = 12345):
    print(f"\n⚡ [CLIENTE gRPC] Ejecutando RPC Unario para matrícula {matricula}...")
    start_time = time.perf_counter()
    
    with get_channel() as channel:
        stub = analytics_pb2_grpc.AnalyticsServiceStub(channel)
        request = analytics_pb2.StudentMetricsRequest(matricula=matricula)
        response = stub.GetStudentMetrics(request)
        
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    print("\n" + "=" * 55)
    print("📥 RESPUESTA PROTOBUF RECIBIDA (Decodificada):")
    print(f"   👤 Matrícula : {response.matricula}")
    print(f"   📛 Nombre    : {response.nombre}")
    print(f"   📊 Promedio  : {response.promedio:.1f}")
    print(f"   ✅ Aprobadas : {response.materias_aprobadas}")
    print(f"   ❌ Reprobadas: {response.materias_reprobadas}")
    print(f"   🏆 Desempeño : {response.nivel_desempeno}")
    print(f"   ⏱️  Latencia  : {elapsed_ms:.2f} ms (Cálculo interno: {response.latencia_calculo_microsegundos} µs)")
    print("=" * 55 + "\n")


def test_streaming(total_eventos: int = 5, intervalo_ms: int = 800):
    print(f"\n📡 [CLIENTE gRPC] Iniciando conexión Server Streaming ({total_eventos} eventos)...")
    print("   (La conexión HTTP/2 permanece abierta mientras el servidor transmite)\n")
    
    with get_channel() as channel:
        stub = analytics_pb2_grpc.AnalyticsServiceStub(channel)
        request = analytics_pb2.TelemetryRequest(
            campus_id="UAdeC-Saltillo",
            total_eventos=total_eventos,
            intervalo_ms=intervalo_ms
        )
        
        response_stream = stub.StreamCampusTelemetry(request)
        
        for event in response_stream:
            print(f"   🔴 [Frame #{event.sequence_id}] {event.sensor} -> {event.valor} {event.unidad} | Estado: {event.estado} | {event.timestamp}")
            
    print("\n✅ Stream finalizado por el servidor.\n")


def test_benchmark(num_requests: int = 100):
    print(f"\n🚀 [BENCHMARK gRPC] Ejecutando {num_requests} llamadas RPC consecutivas...")
    
    with get_channel() as channel:
        stub = analytics_pb2_grpc.AnalyticsServiceStub(channel)
        start_time = time.perf_counter()
        
        for i in range(num_requests):
            req = analytics_pb2.StudentMetricsRequest(matricula=12345 + (i % 3))
            _ = stub.GetStudentMetrics(req)
            
        total_time = time.perf_counter() - start_time
        avg_latency_ms = (total_time / num_requests) * 1000
        req_per_sec = num_requests / total_time
        
        print("\n" + "=" * 55)
        print("📊 RESULTADOS DEL BENCHMARK gRPC (Protobuf):")
        print(f"   Total peticiones   : {num_requests}")
        print(f"   Tiempo total       : {total_time:.3f} s")
        print(f"   Latencia promedio  : {avg_latency_ms:.3f} ms / petición")
        print(f"   Throughput         : {req_per_sec:.1f} req/seg")
        print("=" * 55 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente gRPC para Práctica 2.3")
    parser.add_argument("--unary", action="store_true", help="Ejecutar llamada RPC Unaria")
    parser.add_argument("--matricula", type=int, default=12345, help="Matrícula para prueba unaria")
    parser.add_argument("--stream", action="store_true", help="Ejecutar Server Streaming")
    parser.add_argument("--total", type=int, default=5, help="Número de eventos en streaming")
    parser.add_argument("--benchmark", action="store_true", help="Ejecutar prueba de rendimiento")
    parser.add_argument("--requests", type=int, default=100, help="Número de peticiones para benchmark")
    
    args = parser.parse_args()
    
    if args.stream:
        test_streaming(total_eventos=args.total)
    elif args.benchmark:
        test_benchmark(num_requests=args.requests)
    else:
        test_unary(matricula=args.matricula)
