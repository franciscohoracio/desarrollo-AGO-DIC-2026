# 1. Usar imagen base ligera oficial de Python
FROM python:3.11-slim

# 2. Definir directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Optimización de caché: copiar e instalar dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código de la aplicación
COPY . .

# 5. Documentar el puerto de la aplicación
EXPOSE 8000

# 6. Comando de arranque de FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
