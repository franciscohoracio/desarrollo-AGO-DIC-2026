# Imagen ligera de Python para desarrollo y CI
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y las pruebas
COPY . .

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV ACADEMIC_AUDIT_KEY="UAdeC-CI-SECRET-KEY-2026"

EXPOSE 8000

# Por defecto levanta la API con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
