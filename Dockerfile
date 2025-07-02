FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar driver de MariaDB para Python
RUN pip install mariadb

# Crear directorio de trabajo
WORKDIR /workspace

# Configurar entrypoint para recibir comandos dinámicos
ENTRYPOINT ["/bin/bash", "-c"] 