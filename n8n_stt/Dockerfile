# --- STADIO 1: COSTRUZIONE (BUILDER STAGE) ---
# Questo stadio usa l'immagine base fornita da BUILD_FROM (da build.yaml)
# Qui installeremo tutte le dipendenze Python e prepareremo i tuoi script.
ARG BUILD_FROM
FROM ${BUILD_FROM} AS builder

# Imposta la shell per una gestione degli errori più rigorosa
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Aggiorna i pacchetti e installa Python, pip e jq.
# Questi strumenti saranno presenti solo in questo stadio.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installa le dipendenze Python.
# --no-cache-dir riduce la dimensione dei livelli.
# --break-system-packages è necessario quando si installa in un ambiente di sistema Debian.
RUN pip3 install --break-system-packages --no-cache-dir \
    wyoming==1.6.0 \
    httpx==0.28.1

# Copia i tuoi script nello stadio di costruzione
COPY n8n_stt.py .
COPY run.sh .

# Rendi lo script eseguibile (anche se sarà copiato nello stadio finale)
RUN chmod +x run.sh

# --- STADIO 2: ESECUZIONE (RUNTIME STAGE) ---
# Questo stadio sarà l'immagine finale del tuo add-on.
# Usiamo un'immagine Python "slim" per essere il più leggeri possibile.
# Questa immagine contiene solo l'essenziale per eseguire applicazioni Python.
FROM python:3.11-slim-bookworm

# Imposta la shell anche per questo stadio
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Se il tuo 'run.sh' o 'n8n_stt.py' usano 'jq' a runtime, devi installarlo anche qui.
# Altrimenti, puoi ometterlo per risparmiare spazio.
# RUN apt-get update && apt-get install -y jq --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo ciò che è necessario dallo stadio "builder" allo stadio finale:
# 1. Il tuo script Python
# 2. Il tuo script di avvio
# 3. Le librerie Python installate con pip (sono in /usr/local/lib/python3.11/site-packages)
COPY --from=builder /app/n8n_stt.py .
COPY --from=builder /app/run.sh .
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Assicurati che lo script di avvio sia eseguibile anche nello stadio finale
RUN chmod +x run.sh

# Porta esposta
EXPOSE 10300

# Comando di avvio del tuo add-on
CMD ["./run.sh"]