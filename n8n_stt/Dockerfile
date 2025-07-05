# --- STADIO 1: COSTRUZIONE (BUILDER STAGE) ---
# Questo stadio sarà responsabile dell'installazione di Python, pip e tutte le dipendenze
# necessarie per il tuo add-on. L'immagine BUILD_FROM gestirà la compatibilità con l'architettura.
ARG BUILD_FROM
FROM ${BUILD_FROM} AS builder

# Imposta la shell per una gestione degli errori più rigorosa
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Aggiorna i pacchetti e installa le dipendenze di sistema necessarie.
# - python3-pip: Per gestire i pacchetti Python.
# - jq: Necessario per lo script run.sh.
# - build-essential: Cruciale! Fornisce i compilatori C/C++ e altre utilità necessarie
#                    per compilare eventuali dipendenze native di wyoming o httpx.
#                    Sarà presente solo in questo stadio.
# - --no-install-recommends e rm -rf /var/lib/apt/lists/*: Per mantenere l'immagine snella.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    build-essential \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installa le dipendenze Python globalmente.
# --break-system-packages è necessario qui perché stiamo installando su un'immagine Debian completa.
# --no-cache-dir riduce la dimensione dei livelli.
RUN pip3 install --break-system-packages --no-cache-dir \
    wyoming==1.6.0 \
    httpx==0.28.1

# Copia i tuoi script nello stadio di costruzione
COPY n8n_stt.py .
COPY run.sh .

# Rendi lo script eseguibile
RUN chmod +x run.sh

# --- STADIO 2: ESECUZIONE (RUNTIME STAGE) ---
# Questo stadio sarà l'immagine finale del tuo add-on.
# È il più piccolo possibile, contenendo solo ciò che è essenziale per il runtime.
FROM python:3.11-slim-bookworm

# Imposta la shell anche per questo stadio
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Installa jq anche nello stadio finale, dato che il tuo run.sh lo usa a runtime.
# Non abbiamo bisogno di build-essential qui.
RUN apt-get update && apt-get install -y \
    jq \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia i tuoi script applicativi dallo stadio 'builder'
COPY --from=builder /app/n8n_stt.py .
COPY --from=builder /app/run.sh .

# Copia le librerie Python installate dallo stadio 'builder'.
# Ci assicuriamo di copiare sia site-packages che dist-packages per massima compatibilità,
# dato che la struttura esatta può variare leggermente tra ambienti Debian.
# In genere, per pacchetti installati da pip, saranno in site-packages.
#COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/lib/python3.11/dist-packages /usr/local/lib/python3.11/dist-packages

# Assicurati che lo script di avvio sia eseguibile anche nello stadio finale
RUN chmod +x run.sh

# Porta esposta
EXPOSE 10300

# Comando di avvio del tuo add-on
CMD ["./run.sh"]