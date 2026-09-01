FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y protos
COPY . .

# Compilar los archivos .proto a código Python de Protobuf y gRPC
RUN python -m grpc_tools.protoc -Iprotos --python_out=. --grpc_python_out=. protos/analytics.proto

EXPOSE 50051

CMD ["python", "server.py"]
