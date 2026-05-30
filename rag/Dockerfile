FROM python:3.11-slim

WORKDIR /rag

# Instalar dependencias del sistema para psycopg2 y cliente psql
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src .


# Ensure reset script is executable inside the container
RUN chmod +x reset.sh

CMD ["tail", "-f", "/dev/null"]
