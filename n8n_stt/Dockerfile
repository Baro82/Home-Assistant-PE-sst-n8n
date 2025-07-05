# --- STADIO 1: PREPARAZIONE DELLE DIPENDENZE (BUILDER STAGE) ---
# Questo stadio serve solo a scaricare e preparare le dipendenze Python.
# Non includerà tutti gli strumenti di sviluppo nell'immagine finale.
ARG BUILD_FROM
FROM ${BUILD_FROM} AS builder_deps

# Installa pip per gestire le dipendenze.
# Usiamo --no-install-recommends per mantenere l'immagine il più piccola possibile.
RUN apt-get update && apt-get install -y \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/deps

# Crea un file requirements.txt temporaneo per le tue dipendenze
RUN echo "wyoming==1.6.0" > requirements.txt
RUN echo "httpx==0.28.1" >> requirements.txt

# Scarica le dipendenze in una cartella, senza installarle nel sistema dello stadio builder_deps.
# Questo le rende disponibili per lo stadio successivo.
RUN pip3 download -d . -r requirements.txt

# --- STADIO 2: ESECUZIONE (RUNTIME STAGE) ---
# Questo stadio sarà l'immagine finale del tuo add-on.
# Usiamo un'immagine Python "slim" per essere il più leggeri possibile.
FROM python:3.11-slim-bookworm

# Imposta la shell per una gestione degli errori più rigorosa
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Installazione di jq nello stadio di esecuzione
# È necessario se run.sh o n8n_stt.py lo utilizzano.
RUN apt-get update && apt-get install -y \
    jq \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia i tuoi script applicativi
COPY n8n_stt.py .
COPY run.sh .

# Rendi lo script eseguibile
RUN chmod +x run.sh

# Copia le dipendenze Python scaricate dallo stadio 'builder_deps'
# e poi installale direttamente nell'immagine finale.
COPY --from=builder_deps /tmp/deps /tmp/deps
RUN pip3 install --no-cache-dir /tmp/deps/*

# Porta esposta
EXPOSE 10300

# Comando di avvio del tuo add-on
CMD ["./run.sh"]