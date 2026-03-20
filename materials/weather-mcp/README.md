# MCP Server for Yandex Weather

## Requirements

### For local execution:

- Python 3.10 or higher
- pip (Python package manager)

### For running in Docker:

- Docker 20.10 or higher. 
Official installation guide [is here](https://docs.docker.com/engine/install/).

**Note:** The following examples use Docker 28.5.1 — the CLI interface may differ.

---

### Setup

1. Copy the entire source code to the server
2. Configure the `.env` file
    1. If it doesn't exist, create one (e.g., `cp .env.example .env`)
    2. Set the value for the `WEATHER_API_KEY` environment variable — this is the API key from your personal account on Yandex.Weather

### Running the application

#### 1. Build Docker image

```bash
docker build -t mcp-server:latest .
```

#### 2. Run Docker container

```bash
docker run -d -p 8000:8000 --name mcp-server --env-file=.env mcp-server:latest
```

#### 3. Check Docker container

Check the container status in the list:

```bash
docker ps -a
```

Find the container named `mcp-server`. Its status should be "healthy". If the status is "healthy (starting)", wait 5–10 seconds and check again.

Also, view the server logs:

```bash
docker logs mcp-server
```

Server logs should look similar to this example:

```
INFO     Starting MCP server 'MCP-сервер    transport.py:273
                             для прогноза погоды' with                          
                             transport 'streamable-http' on                     
                             http://0.0.0.0:8000/mcp                            
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     172.17.0.1:42916 - "OPTIONS /sse HTTP/1.1" 404 Not Found
INFO:     172.17.0.1:42922 - "OPTIONS /sse HTTP/1.1" 404 Not Found
```

> **Note**: If you need to modify the container (correct code, update environment variables, etc.), you'll need to rebuild the image. Stop and remove the container, then repeat all the steps in this section.

---

## Helpers

### Installing and running MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run the inspector
npx @modelcontextprotocol/inspector
```

### Copy a folder to the server using scp
```bash
scp -r <local_folder_path> <user_name>@<ip_address>:<server_folder_path>
```
