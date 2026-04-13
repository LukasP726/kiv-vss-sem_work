FROM eclipse-temurin:21-jre

ARG NETLOGO_VERSION=7.0.3
ARG NETLOGO_ARCHIVE=NetLogo-${NETLOGO_VERSION}-64.tgz
ARG NETLOGO_URL=https://downloads.netlogo.org/${NETLOGO_VERSION}/${NETLOGO_ARCHIVE}

ENV DEBIAN_FRONTEND=noninteractive
ENV NETLOGO=/opt/NetLogo-${NETLOGO_VERSION}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-pip python-is-python3 make ca-certificates curl tar \
       xauth libgtk-3-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 libasound2t64 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt \
    && curl -fsSL "${NETLOGO_URL}" -o "/tmp/${NETLOGO_ARCHIVE}" \
    && tar -xzf "/tmp/${NETLOGO_ARCHIVE}" -C /opt \
    && if [ -d "/opt/NetLogo ${NETLOGO_VERSION}" ] && [ ! -d "${NETLOGO}" ]; then mv "/opt/NetLogo ${NETLOGO_VERSION}" "${NETLOGO}"; fi \
    && sed -i 's/[[:space:]]\+\[\][[:space:]]*)/)/' "${NETLOGO}/netlogo-headless.sh" \
    && rm -f "/tmp/${NETLOGO_ARCHIVE}" \
    && chmod +x "${NETLOGO}/netlogo-headless.sh"

WORKDIR /workspace
COPY . /workspace
VOLUME ["/workspace/out"]

CMD ["make", "baseline"]
