ARG BUILD_FROM=alpine:3.22.0
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]


# Install base system
ARG BUILD_ARCH=amd64
ARG BASHIO_VERSION="v0.17.0"
ARG S6_OVERLAY_VERSION="3.2.1.0"
ARG TEMPIO_VERSION="2024.11.2"
RUN \
    set -o pipefail \
    \
    && apk add --no-cache --virtual .build-dependencies \
        tar=1.35-r3 \
        xz=5.8.1-r0 \
    \
    && apk add --no-cache \
        libcrypto3=3.5.1-r0 \
        libssl3=3.5.1-r0 \
        musl-utils=1.2.5-r10 \
        musl=1.2.5-r10 \
    \
    && apk add --no-cache \
        bash=5.2.37-r0 \
        curl=8.14.1-r1 \
        jq=1.8.0-r0 \
        tzdata=2025b-r0 \
    \
    && S6_ARCH="${BUILD_ARCH}" \
    && if [ "${BUILD_ARCH}" = "i386" ]; then S6_ARCH="i686"; \
    elif [ "${BUILD_ARCH}" = "amd64" ]; then S6_ARCH="x86_64"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then S6_ARCH="arm"; fi \
    \
    && curl -L -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz" \
        | tar -C / -Jxpf - \
    \
    && curl -L -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz" \
        | tar -C / -Jxpf - \
    \
    && curl -L -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-noarch.tar.xz" \
        | tar -C / -Jxpf - \
    \
    && curl -L -s "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-arch.tar.xz" \
        | tar -C / -Jxpf - \
    \
    && curl -J -L -o /tmp/bashio.tar.gz \
        "https://github.com/hassio-addons/bashio/archive/${BASHIO_VERSION}.tar.gz" \
    && mkdir /tmp/bashio \
    && tar zxvf \
        /tmp/bashio.tar.gz \
        --strip 1 -C /tmp/bashio \
    \
    && mv /tmp/bashio/lib /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio \
    \
    && curl -L -s -o /usr/bin/tempio \
        "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/tempio \
    \
    && apk del --no-cache --purge .build-dependencies \
    && rm -f -r \
        /tmp/*


RUN apk add --no-cache \
        python3 \
        python3-pip

# Copy root filesystem
COPY rootfs /

# Copy s6-overlay adjustments
COPY s6-overlay /package/admin/s6-overlay-${S6_OVERLAY_VERSION}/


WORKDIR /app

RUN pip3 install --break-system-packages --no-cache-dir wyoming==1.6.0 httpx==0.28.1


COPY n8n_stt.py .
COPY run.sh .

RUN chmod +x run.sh

EXPOSE 10300

CMD ["./run.sh"]