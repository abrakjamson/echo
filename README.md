# Echo Server

A lightweight, publicly available Azure Functions application for testing protocol implementations. The server echoes back requests using multiple protocol bindings: HTTP/REST, JSON-RPC, MCP (Model Context Protocol), and Agent2Agent (A2A).

## Purpose

This server provides a simple, reliable endpoint for developers to test and validate their protocol client implementations. Each endpoint echoes back the input data, making it easy to verify that your client is constructing and sending requests correctly.

## Public URL

```
https://echo.azurewebsites.net/api/
```

## Endpoints

### 1. Echo Endpoint (`/echo`)

Simple HTTP echo service. Accepts a value and returns it as plain text.

**Request Methods**: GET, POST

**Parameters**:
- Query parameter: `?value=<text>`
- Or JSON body: `{"value": "<text>"}`

#### curl Example

```bash
# Using query parameter
curl "https://echo.azurewebsites.net/api/echo?value=hello"

# Using JSON body
curl -X POST "https://echo.azurewebsites.net/api/echo" \
  -H "Content-Type: application/json" \
  -d '{"value": "hello"}'
```

#### PowerShell Example

```powershell
# Using query parameter
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/echo?value=hello"

# Using JSON body
$body = @{ value = "hello" } | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/echo" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 2. JSON-RPC Endpoint (`/jsonrpc`)

JSON-RPC 1.0 and 2.0 protocol handler. Echoes back the entire request in the response result field.

**Request Method**: POST

**Supports**:
- JSON-RPC 1.0 (no `jsonrpc` field required)
- JSON-RPC 2.0 (requires `jsonrpc: "2.0"`)
- Notifications (JSON-RPC 2.0 without `id`)

#### curl Examples

```bash
# JSON-RPC 1.0 with named params
curl -X POST "https://echo.azurewebsites.net/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"method":"test_method","params":{"key":"value"},"id":"1"}'

# JSON-RPC 2.0 with array params
curl -X POST "https://echo.azurewebsites.net/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"test_method","params":[1,2,3],"id":1}'

# JSON-RPC 2.0 notification (no id)
curl -X POST "https://echo.azurewebsites.net/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"notify_method","params":{}}'
```

#### PowerShell Examples

```powershell
# JSON-RPC 1.0 with named params
$body = @{
    method = "test_method"
    params = @{ key = "value" }
    id = "1"
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/jsonrpc" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# JSON-RPC 2.0 with array params
$body = @{
    jsonrpc = "2.0"
    method = "test_method"
    params = @(1, 2, 3)
    id = 1
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/jsonrpc" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# JSON-RPC 2.0 notification (no id)
$body = @{
    jsonrpc = "2.0"
    method = "notify_method"
    params = @{}
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/jsonrpc" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 3. MCP Endpoint (`/mcp`)

Model Context Protocol handler. Echoes back the request in the response result field.

**Request Method**: POST

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/mcp" \
  -H "Content-Type: application/json" \
  -d '{"action":"echo","payload":{"key":"value"},"id":1}'
```

#### PowerShell Example

```powershell
$body = @{
    action = "echo"
    payload = @{ key = "value" }
    id = 1
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/mcp" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 4. Agent2Agent (A2A) SendMessage Endpoint (`/message:send`)

Agent2Agent Protocol v1.0.0 HTTP/REST binding. Accepts A2A Message objects and echoes back the message content in a new agent-role Message response.

**Request Method**: POST

**Spec**: [A2A Protocol v1.0.0](https://a2a-protocol.org/)

**Message Fields**:
- `messageId` (string): Unique identifier for the message
- `role` (enum): `"user"` or `"agent"`
- `parts` (array): Message content (TextPart, FilePart, etc.)
- `metadata` (object, optional): Additional metadata

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/message:send" \
  -H "Content-Type: application/json" \
  -d '{
    "messageId": "msg-001",
    "role": "user",
    "parts": [{"text": "Hello, agent!"}],
    "metadata": {"source": "client"}
  }'
```

#### PowerShell Example

```powershell
$body = @{
    messageId = "msg-001"
    role = "user"
    parts = @(
        @{ text = "Hello, agent!" }
    )
    metadata = @{ source = "client" }
} | ConvertTo-Json -Depth 10
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/message:send" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 5. Agent Card Discovery Endpoint (`/.well-known/agent-card.json`)

A2A agent card for service discovery. Returns metadata about the echo server including the SendMessage endpoint.

**Request Method**: GET

#### curl Example

```bash
curl "https://echo.azurewebsites.net/api/.well-known/agent-card.json"
```

#### PowerShell Example

```powershell
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/.well-known/agent-card.json"
```

---

## Testing Locally

### Setup

```bash
cd echo_functions
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run Unit & Integration Tests

```bash
# Tests local handlers + deployed endpoints
python test_endpoints.py
```

### Test Production Endpoints

```bash
# Tests only the deployed production endpoints
python test_production.py
```

## Use Cases

- **Protocol Testing**: Validate your JSON-RPC, MCP, or A2A client implementations
- **Integration Testing**: Test client-server communication with a reliable echo service
- **Documentation**: Use curl/PowerShell examples in your client documentation
- **Debugging**: Verify request payloads are constructed correctly
- **CI/CD**: Include endpoint tests in your pipeline

## License

This echo server is provided as a public testing utility.
