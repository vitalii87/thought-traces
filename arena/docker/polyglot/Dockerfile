ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        cargo \
        clang \
        cmake \
        fp-compiler \
        golang-go \
        jq \
        openjdk-17-jdk-headless \
        python3 \
        rustc \
        time \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 iah \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/sh iah

COPY toolchain-report.sh /usr/local/bin/iah-toolchain-report
RUN chmod 0555 /usr/local/bin/iah-toolchain-report

USER 1000:1000
WORKDIR /workspace

CMD ["iah-toolchain-report"]
