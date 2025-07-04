#!/bin/sh

# Read N8N_WEBHOOK_URL from Home Assistant options
#N8N_WEBHOOK_URL=$(bashio::config 'N8N_WEBHOOK_URL')
N8N_WEBHOOK_URL=$(jq -r '.N8N_WEBHOOK_URL' /data/options.json)

# Export as environment variable
export N8N_WEBHOOK_URL

# Start the STT server
python3 /app/n8n_stt.py