FROM node:slim@sha256:aa27a5fbf5acb298116a38133794f080406c6f8dfe52e2e2836bb55dc7cae8f0 AS base

FROM base AS installation

RUN apt-get update && apt-get install -y \
   git \
   curl \
   bash \
   python3 \
   build-essentials \
   && rm -rf /var/lib/apt/lists/*

RUN npm install -g @google/gemini-cli

WORKDIR /workspace

ENTRYPOINT ["gemini"]
