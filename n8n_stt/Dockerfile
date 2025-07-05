# --- STADIO 1: Preparazione del Codice (solo per copiare i tuoi script) ---
# Usiamo l'immagine base del tuo build.yaml. Qui non installeremo Python o altre dipendenze.
ARG BUILD_FROM
FROM ${BUILD_FROM} AS builder

WORKDIR /app

# Copia i tuoi script in questo stadio temporaneo
COPY n8n_stt.py .
COPY run.sh .

# Rendiamo lo script eseguibile qui (la copia lo manterrà eseguibile)
RUN chmod +x run.sh

# --- STADIO 2: Esecuzione (RUNTIME STAGE) ---
# Questa sarà l'immagine finale del tuo add-on.
# È il più piccolo possibile, contenendo solo ciò che è essenziale per il runtime.
FROM python:3.11-slim-bookworm

# Imposta la shell per una gestione degli errori più rigorosa
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Installa le dipendenze di sistema necessarie per il runtime:
# - jq: Necessario perché il tuo script run.sh lo utilizza.
# - python3-pip: Necessario per installare le dipendenze Python in questo stadio.
# --no-install-recommends e rm -rf /var/lib/apt/lists/*: Per mantenere l'immagine snella.
RUN apt-get update && apt-get install -y \
    jq \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia i tuoi script applicativi dallo stadio 'builder'
COPY --from=builder /app/n8n_stt.py .
COPY --from=builder /app/run.sh .

# Installa le dipendenze Python direttamente in questo stadio.
# Questo garantisce che vengano posizionate correttamente per l'interprete Python dell'immagine slim.
# Non è necessario --break-system-packages qui, dato che siamo su un'immagine Python ufficiale.
RUN pip3 install --no-cache-dir \
    wyoming==1.6.0 \
    httpx==0.28.1

# Assicurati che lo script di avvio sia eseguibile anche nello stadio finale
RUN chmod +x run.sh

# Porta esposta
EXPOSE 10300

# Comando di avvio del tuo add-on
CMD ["./run.sh"]