#!/usr/bin/env python3

import os
import sys

from fastmcp import FastMCP

from weather_requester.builder import build_request_type_to_requester


def make_weather_mcp() -> FastMCP:
    api_key = os.getenv('WEATHER_API_KEY')
    if api_key is None or api_key == '':
        sys.exit('Env WEATHER_API_KEY must be filled')

    mcp = FastMCP(
        name="MCP-сервер для прогноза погоды",
        version="1.0.0",
    )

    request_type_to_requester = build_request_type_to_requester(api_key=api_key)
    for request_type, requester in request_type_to_requester.items():
        mcp.tool(name_or_fn=request_type)(requester.request)

    return mcp


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    print(f"Starting MCP Server with transport: {transport}")
    if transport in ("sse", "streamable-http"):
        print(f"Server will be available at: http://{host}:{port}")
        if transport == "sse":
            print(f"SSE endpoint: http://{host}:{port}/sse")
        else:
            print(f"MCP endpoint: http://{host}:{port}/mcp")

    weather_mcp = make_weather_mcp()
    weather_mcp.run(transport=transport, host=host, port=port)
