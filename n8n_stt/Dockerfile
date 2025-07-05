ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.0.2
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]


RUN \
    apk add --no-cache --virtual .build-dependencies \
        build-base=0.5-r3 \
        py3-pip=25.1.1-r0 \
        python3-dev=3.12.11-r0 \
    \
    && apk add --no-cache \
        py3-pip=25.1.1-r0 \
        python3=3.12.11-r0 

RUN pip3 install --break-system-packages --no-cache-dir wyoming==1.6.0 httpx==0.28.1


WORKDIR /app


COPY n8n_stt.py .
COPY run.sh .

RUN chmod +x run.sh

EXPOSE 10300

CMD ["./run.sh"]