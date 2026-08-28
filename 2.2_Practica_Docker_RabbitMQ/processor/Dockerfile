# 1. Imagen base ligera de Python
FROM python:3.11-slim

# 2. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalación de dependencias con caché optimizado
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar código fuente
COPY . .

# 5. Evita que Python bufferice los prints en consola para ver logs en tiempo real
ENV PYTHONUNBUFFERED=1

# 6. Ejecución del script procesador
CMD ["python", "processor.py"]
