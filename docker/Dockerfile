FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rcon_client/ rcon_client/
COPY mcp_server/ mcp_server/
ENV FACTORIO_HOST=host.docker.internal FACTORIO_PORT=27015
CMD ["python", "-m", "mcp_server.server"]
