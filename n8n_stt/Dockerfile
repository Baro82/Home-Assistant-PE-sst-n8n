ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        jq \
#        python3 \
#        python3-pip \
#        build-essential \
#        libffi-dev \
#        libssl-dev \
#        rustc \
#        cargo \
#    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y python3 python3-pip jq

WORKDIR /app

RUN pip3 install --break-system-packages --no-cache-dir wyoming==1.6.0 httpx==0.28.1


COPY n8n_stt.py .
COPY run.sh .

RUN chmod +x run.sh

EXPOSE 10300

CMD ["./run.sh"]
