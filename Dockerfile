# Imagen base con Python
FROM python:3.11-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Instalar dependencias del sistema (para mysqlclient)
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev && \
    apt-get clean

# Crear carpeta de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto
EXPOSE 8050

# Comando para arrancar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8050"]