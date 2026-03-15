# Echo Server with JSON-RPC, MCP, and Agent2Agent Support

A lightweight Azure Functions application that provides HTTP echo, JSON-RPC, MCP (Model Context Protocol), and Agent2Agent (A2A) protocol endpoints.

## Public URL

```
https://echo.azurewebsites.net/api/
```

## Project Structure

```
echo_functions/
├── function_app.py          # Azure Functions app with all protocol routes
├── jsonrpc_handler.py       # JSON-RPC 1.0 and 2.0 protocol handler
├── mcp_handler.py           # MCP (Model Context Protocol) handler
├── a2a_handler.py           # A2A HTTP/REST protocol handler
├── a2a_jsonrpc_handler.py   # A2A JSON-RPC protocol handler
├── test_endpoints.py        # Comprehensive test suite (local + HTTP)
├── test_production.py       # Production endpoint validation script
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions configuration
└── .venv/                  # Virtual environment (local)
```

### Key Files

**function_app.py**
- `@app.route("echo")` - HTTP echo endpoint (GET/POST)
- `@app.route("jsonrpc")` - Standard JSON-RPC 1.0/2.0 endpoint
- `@app.route("mcp")` - MCP (Model Context Protocol) endpoint
- `@app.route("a2a/message:send")` - A2A SendMessage (HTTP/REST)
- `@app.route("a2a/tasks/...")` - A2A Task operations (Get, List, Cancel)
- `@app.route("a2a")` - A2A Protocol JSON-RPC 2.0 binding
- `@app.route(".well-known/agent-card.json")` - A2A Agent Card discovery

**a2a_handler.py**
- `A2AHandler.handle_request(req_body)` - A2A REST logic
  - Parses A2A Message objects using `a2a-sdk`
  - Echoes content back in a new Message response
  - Implements `GetTask`, `ListTasks`, and `CancelTask` stubs
  - Follows A2A Protocol v1.0.0 specification

**a2a_jsonrpc_handler.py**
- `A2AJsonRpcHandler.handle_request(req_body)` - A2A JSON-RPC binding
  - Maps JSON-RPC methods (`a2a.SendMessage`, etc.) to A2A operations
  - Returns responses in proper JSON-RPC 2.0 format

**jsonrpc_handler.py**
- `JsonRpcHandler.handle_request(req_body)` - Standard JSON-RPC handler
  - Detects JSON-RPC version (1.0 or 2.0)
  - Returns compliant echo responses

**mcp_handler.py**
- `McpHandler.handle_request(req_body)` - MCP protocol handler
  - Implements JSON-RPC 2.0 compliant responses
  - Echoes `method` and `params` in the `result` field
  - Supports MCP `initialize` lifecycle method
  - Handles JSON-RPC notifications (no response)

## How to Test

### Local Testing

1. **Setup local environment**
   ```bash
   cd echo_functions
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the test suite**
   ```bash
   python test_endpoints.py
   ```
   
   This runs:
   - Handler unit tests for JSON-RPC, MCP, and A2A
   - Local verification of A2A Message structures using the SDK
   - Live HTTP integration tests for all deployed endpoints

### Manual Testing with curl (A2A REST)

**Test A2A SendMessage**
```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a/message:send" \
  -H "Content-Type: application/json" \
  -d '{
    "messageId": "msg-001",
    "role": "user",
    "parts": [{"text": "hello from A2A client"}],
    "metadata": {"source": "test"}
  }'
```

**Test A2A JSON-RPC**
```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "a2a.SendMessage",
    "params": {
      "message": {
        "messageId": "msg-002",
        "role": "user",
        "parts": [{"text": "hello via JSON-RPC"}]
      }
    },
    "id": 1
  }'
```

**Test MCP**
```bash
curl -X POST "https://echo.azurewebsites.net/api/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "echo",
    "params": {"test": "data"},
    "id": 1
  }'
```

### Production Testing

Run the dedicated production test suite to verify the live environment:

```bash
python test_production.py
```

## Features

✅ **Multi-Protocol Support**
- Standard HTTP Echo
- JSON-RPC 1.0 & 2.0
- Model Context Protocol (MCP)
- Agent2Agent (A2A) v1.0.0

✅ **A2A HTTP/REST Binding**
- `POST /a2a/message:send`
- `GET /a2a/tasks/{id}`
- `GET /a2a/tasks`
- `POST /a2a/tasks/{id}:cancel`

✅ **A2A JSON-RPC Binding**
- Full `a2a.*` method mapping at `/api/a2a`

✅ **Discovery**
- RFC 8288 compliant `.well-known/agent-card.json`

✅ **Validation**
- Comprehensive local and production test coverage
- Strict A2A Message schema validation using `a2a-sdk`
