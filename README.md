# Echo Server

A lightweight, publicly available Azure Functions application for testing protocol implementations. The server echoes back requests using multiple protocol bindings: HTTP/REST, SOAP, JSON-RPC, MCP (Model Context Protocol), and Agent2Agent (A2A).

## Purpose

This server provides a simple, reliable endpoint for developers to test and validate their protocol client implementations. Each endpoint echoes back the input data, making it easy to verify that your client is constructing and sending requests correctly.

## Public URL

```
https://echo.azurewebsites.net/api/
```

## Table of Contents

- [Endpoints](#endpoints)
  - [Echo](#1-echo-endpoint-echo)
  - [SOAP](#2-soap-endpoint-soap)
  - [JSON-RPC](#3-json-rpc-endpoint-jsonrpc)
  - [MCP](#4-mcp-endpoint-mcp)
  - [MCP SSE](#mcp-sse-endpoint-mcp-sse)
  - [A2A JSON-RPC](#5-agent2agent-a2a-json-rpc-endpoint-a2a)
  - [A2A HTTP/REST](#6-agent2agent-a2a-httprest-endpoints-a2a)
  - [Agent Card](#7-agent-card-discovery-endpoint-well-knownagent-cardjson)
- [Testing Locally](#testing-locally)
- [Use Cases](#use-cases)
- [License](#license)

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

### 2. SOAP Endpoint (`/soap`)

SOAP 1.1 protocol echo handler. Parses a SOAP 1.1 Envelope and echoes back the content of the first element in the Body within a corresponding Response tag.

**Request Method**: POST

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/soap" \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:echo="http://example.com/echo">
   <soapenv:Header/>
   <soapenv:Body>
      <echo:EchoRequest>
         <echo:Message>Hello, SOAP!</echo:Message>
      </echo:EchoRequest>
   </soapenv:Body>
</soapenv:Envelope>'
```

#### PowerShell Example

```powershell
$xml = @"
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:echo="http://example.com/echo">
   <soapenv:Header/>
   <soapenv:Body>
      <echo:EchoRequest>
         <echo:Message>Hello, SOAP!</echo:Message>
      </echo:EchoRequest>
   </soapenv:Body>
</soapenv:Envelope>
"@

Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/soap" `
  -Method Post `
  -ContentType "text/xml" `
  -Body $xml
```

---

### 3. JSON-RPC Endpoint (`/jsonrpc`)

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

### 4. MCP Endpoint (`/mcp`)

Model Context Protocol (MCP) handler. Implements the MCP specification using JSON-RPC 2.0. Echoes back the `method` and `params` in the response `result` field.

**Request Method**: POST

**Spec**: [Model Context Protocol](https://modelcontextprotocol.io/)

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"echo","params":{"key":"value"},"id":1}'
```

#### PowerShell Example

```powershell
$body = @{
    jsonrpc = "2.0"
    method = "echo"
    params = @{ key = "value" }
    id = 1
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/mcp" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

#### MCP SSE Endpoint (`/mcp/sse`)

A Server-Sent Events (SSE) stream endpoint that emits MCP-compliant JSON-RPC messages as SSE events. The server responds with an `event: message` stream containing the JSON-RPC response payload.

**Request Method**: POST

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/mcp/sse" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"echo","params":{"key":"value"},"id":1}'
```

#### PowerShell Example

```powershell
$body = @{
    jsonrpc = "2.0"
    method = "echo"
    params = @{ key = "value" }
    id = 1
} | ConvertTo-Json
Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/mcp/sse" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 5. Agent2Agent (A2A) JSON-RPC Endpoint (`/a2a`)

Agent2Agent Protocol v1.0.0 JSON-RPC 2.0 binding. Implements A2A operations using JSON-RPC 2.0 as the transport mechanism.

**Request Method**: POST

**Spec**: [A2A Protocol v1.0.0](https://a2a-protocol.org/)

**Supported Methods**:
- `a2a.SendMessage`: Send a message to the agent and get a response
- `a2a.GetTask`: Retrieve task state (stub for echo server)
- `a2a.ListTasks`: List all tasks (stub for echo server, returns empty)
- `a2a.CancelTask`: Cancel a task (stub for echo server)

#### JSON-RPC Method: a2a.SendMessage

Sends an A2A Message object via JSON-RPC 2.0 and receives an echoed response.

**Request Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "a2a.SendMessage",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "user",
      "parts": [{"text": "Hello, agent!"}],
      "metadata": {"source": "client"}
    }
  },
  "id": 1
}
```

#### curl Example

```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "a2a.SendMessage",
    "params": {
      "message": {
        "messageId": "msg-001",
        "role": "user",
        "parts": [{"text": "Hello, agent!"}],
        "metadata": {"source": "client"}
      }
    },
    "id": 1
  }'
```

#### PowerShell Example

```powershell
$message = @{
    messageId = "msg-001"
    role = "user"
    parts = @(
        @{ text = "Hello, agent!" }
    )
    metadata = @{ source = "client" }
}

$body = @{
    jsonrpc = "2.0"
    method = "a2a.SendMessage"
    params = @{ message = $message }
    id = 1
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "https://echo.azurewebsites.net/api/a2a" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

### 6. Agent2Agent (A2A) HTTP/REST Endpoints (`/a2a/...`)

Agent2Agent Protocol v1.0.0 HTTP/REST binding. Provides a set of RESTful endpoints for message and task operations.

**Spec**: [A2A Protocol v1.0.0](https://a2a-protocol.org/)

#### POST `/a2a/message:send` (SendMessage)

Accepts A2A Message objects and echoes back the message content in a new agent-role Message response.

**curl Example**:
```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a/message:send" \
  -H "Content-Type: application/json" \
  -d '{
    "messageId": "msg-001",
    "role": "user",
    "parts": [{"text": "Hello, agent!"}],
    "metadata": {"source": "client"}
  }'
```

#### GET `/a2a/tasks/{id}` (GetTask)

Retrieves the status of a specific task. Returns a completed stub for testing.

**curl Example**:
```bash
curl "https://echo.azurewebsites.net/api/a2a/tasks/task-123"
```

#### GET `/a2a/tasks` (ListTasks)

Lists all tasks. Returns an empty list placeholder for the echo server.

**curl Example**:
```bash
curl "https://echo.azurewebsites.net/api/a2a/tasks"
```

#### POST `/a2a/tasks/{id}:cancel` (CancelTask)

Cancels a specific task. Returns a canceled status stub for testing.

**curl Example**:
```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a/tasks/task-123:cancel"
```

---

### 7. Agent Card Discovery Endpoint (`/.well-known/agent-card.json`)

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
