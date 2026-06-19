FROM python:3.12-slim
WORKDIR /app
COPY src/spark /app/src/spark
COPY src/biome /app/src/biome
# seed the real-world spatial blocks into the store at build (serve.py adds the constitution on boot)
RUN mkdir -p /data/blocks && cp /app/src/biome/world/earth/*.json /data/blocks/
ENV BIOME_ROOT=/data
# serve.py reads PORT from the platform and binds 0.0.0.0; door + /mcp + /world
CMD ["python3", "src/biome/serve.py"]
