FROM python:3.12-slim

ARG VALE_VERSION=3.14.2

RUN apt-get update \
  && apt-get install -y --no-install-recommends bash git ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN arch="$(dpkg --print-architecture)" \
  && case "${arch}" in \
    amd64) vale_arch="64-bit" ;; \
    arm64) vale_arch="arm64" ;; \
    *) echo "unsupported architecture for Vale: ${arch}" >&2; exit 1 ;; \
  esac \
  && VALE_ARCH="${vale_arch}" python3 -c "import os, urllib.request; version=os.environ['VALE_VERSION']; arch=os.environ['VALE_ARCH']; urllib.request.urlretrieve(f'https://github.com/errata-ai/vale/releases/download/v{version}/vale_{version}_Linux_{arch}.tar.gz', '/tmp/vale.tar.gz')" \
  && tar -xzf /tmp/vale.tar.gz -C /usr/local/bin vale \
  && rm /tmp/vale.tar.gz

WORKDIR /work
COPY . .

CMD ["bash", "scripts/validate.sh"]
