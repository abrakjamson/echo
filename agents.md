# Echo Server with JSON-RPC, MCP, and Agent2Agent Support

A lightweight Azure Functions application that provides HTTP echo, JSON-RPC, MCP (Model Context Protocol), and Agent2Agent (A2A) protocol endpoints.

## Public URL

```
https://echo.azurewebsites.net/api/
```

## Project Structure

```
echo_functions/
├── function_app.py          # Azure Functions app with /echo, /jsonrpc, /mcp, and /a2a routes
├── jsonrpc_handler.py       # JSON-RPC 1.0 and 2.0 protocol handler
├── mcp_handler.py           # MCP (Model Context Protocol) handler
├── a2a_handler.py           # Agent2Agent protocol handler
├── test_endpoints.py        # Comprehensive test suite (local + HTTP)
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions configuration
├── local.settings.json     # Local development settings
└── .venv/                  # Virtual environment (local)
```

### Key Files

**function_app.py**
- `@app.route("echo")` - HTTP echo endpoint (GET/POST)
  - Accepts value via query param or JSON body
  - Returns the echoed value as plain text
  
- `@app.route("jsonrpc", methods=["POST"])` - JSON-RPC endpoint
  - Accepts JSON-RPC 1.0 and 2.0 requests
  - Returns responses with proper protocol compliance
  - Echoes back the full request in the result field

- `@app.route("mcp", methods=["POST"])` - MCP endpoint
  - Accepts MCP requests
  - Echoes back the request in the result field

- `@app.route("a2a", methods=["POST"])` - Agent2Agent endpoint
  - Accepts A2A Protocol messages
  - Returns messages with data echoed back

- `@app.route(".well-known/agent-card.json", methods=["GET"])` - A2A Agent Card endpoint
  - Serves the agent card for A2A Protocol discovery
  - Returns A2A-compliant metadata (name, endpoint, capabilities, skills)
  - Implements A2A Protocol v1.0.0 specification

**jsonrpc_handler.py**
- `JsonRpcHandler.handle_request(req_body)` - Protocol parser and handler
  - Detects JSON-RPC version (1.0 or 2.0)
  - Validates required fields (method, id)
  - Generates proper error responses
  - Returns echo responses

**mcp_handler.py**
- `McpHandler.handle_request(req_body)` - MCP protocol handler

**a2a_handler.py**
- `A2AHandler.handle_request(req_body)` - A2A protocol handler
  - Parses A2A Message objects using a2a-sdk
  - Echoes the data field back in a new Message response
  - Follows A2A Protocol v0.3.0 specification

**test_endpoints.py**
- Local unit tests (handler logic)
- Live HTTP integration tests
- Graceful fallback if endpoints not deployed

**test_production.py**
- Production endpoint tests for https://echo.azurewebsites.net/api/
- Comprehensive validation of all deployed endpoints
- Tests: Echo, JSON-RPC, MCP, A2A, and Agent Card
- Exit code indicates pass/fail for CI/CD integration

## How to Test

### Local Testing

1. **Setup local environment**
   ```bash
   cd echo_functions
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the test suite**
   ```bash
   python test_endpoints.py
   ```
   
   This runs:
   - 5 local unit tests (JSON-RPC handler logic)
   - 2 local unit tests (MCP and A2A handlers)
   - 7 live HTTP integration tests (if endpoints deployed)
   - Endpoint status summary (quick health check for all deployed endpoints)
   - Graceful fallback if endpoints unavailable

3. **Expected output**
   ```
   === Testing JSON-RPC 1.0 ===
   ✓ JSON-RPC 1.0 test passed
   
   === Testing JSON-RPC 2.0 ===
   ✓ JSON-RPC 2.0 test passed
   
   === Testing JSON-RPC 2.0 Notification (no id) ===
   ✓ JSON-RPC 2.0 notification test passed
   
   === Testing Invalid Request ===
   ✓ Invalid request test passed
   
   === Testing Non-Dict Request ===
   ✓ Non-dict request test passed
   
   === Testing HTTP Echo Endpoint ===
   Test 1: Query parameter
   ✓ Query parameter test passed
   
   Test 2: JSON body
   ✓ JSON body test passed
   
   Test 3: Missing value field
   ✓ Missing value test passed
   
   === Testing HTTP JSON-RPC Endpoint ===
   Test 1: JSON-RPC 1.0
   ✓ JSON-RPC 1.0 test passed
   
   Test 2: JSON-RPC 2.0
   ✓ JSON-RPC 2.0 test passed
   
   Test 3: JSON-RPC 2.0 notification (no id)
   ✓ JSON-RPC 2.0 notification test passed
   
   === Testing HTTP MCP Endpoint ===
   Test 1: POST JSON body
   ✓ HTTP MCP endpoint test passed
   
   === Testing HTTP A2A Endpoint ===
   Test 1: A2A message echo
   ✓ HTTP A2A endpoint test passed
   
   ==================================================
   Endpoint Status Summary
   ==================================================
     ✓ Echo         (200)
     ✓ JSON-RPC 2.0 (200)
     ✓ MCP          (200)
     ✓ A2A          (200)
   
   ==================================================
   All tests passed! ✓
   ==================================================
   ```

### Manual Testing with curl

**Test the echo endpoint**
```bash
# Query parameter
curl "https://echo.azurewebsites.net/api/echo?value=hello"

# JSON body
curl -X POST "https://echo.azurewebsites.net/api/echo" \
  -H "Content-Type: application/json" \
  -d '{"value": "world"}'
```

**Test JSON-RPC 2.0**
```bash
curl -X POST "https://echo.azurewebsites.net/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"test","params":[],"id":1}'
```

**Test JSON-RPC 1.0**
```bash
curl -X POST "https://echo.azurewebsites.net/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"method":"test","params":{},"id":"1"}'
```

**Test Agent2Agent (A2A)**
```bash
curl -X POST "https://echo.azurewebsites.net/api/a2a" \
  -H "Content-Type: application/json" \
  -d '{"data":{"message":"hello from A2A client"},"metadata":{"source":"test"}}'
```

**Test Agent Card (A2A Discovery)**
```bash
curl "https://echo.azurewebsites.net/api/.well-known/agent-card.json"
```

### Deployment

Deploy to Azure Functions using the Azure CLI or Azure Functions extension:
```bash
func azure functionapp publish <app-name>
```

### Production Testing

Once deployed, run the production test suite to verify all endpoints are operational:

```bash
python test_production.py
```

This will:
- Test all 5 deployed endpoints (Echo, JSON-RPC, MCP, A2A, Agent Card)
- Verify response status codes (200)
- Validate JSON structures and required fields
- Check agent card compliance with A2A Protocol v1.0.0
- Exit with code 0 if all tests pass, 1 if any fail (useful for CI/CD)

Example output:
```
============================================================
Production Endpoint Status Summary
============================================================
  ✓ Echo            PASS
  ✓ JSON-RPC        PASS
  ✓ MCP             PASS
  ✓ A2A             PASS
  ✓ Agent Card      PASS
============================================================
✓ All production endpoints are operational!
============================================================
```

## Features

✅ **Echo Endpoint**
- Accepts value via query parameter or JSON body
- Returns plain text response

✅ **JSON-RPC 1.0 Support**
- Method, params (object), id fields
- Echo response in result field

✅ **JSON-RPC 2.0 Support**
- Method, params (array or object), id, jsonrpc: "2.0" fields
- Notifications (requests without id)
- Proper error codes (-32600, -32700, -32603)

✅ **Agent2Agent (A2A) Support**
- A2A Protocol v0.3.0 compliant
- Accepts A2A Message objects
- Echoes data back in response Message using official a2a-sdk

✅ **Testing**
- 5 local unit tests for handler logic
- 2 local unit tests for MCP and A2A handlers
- 7 HTTP integration tests for deployed endpoints
- All tests passing ✓

## Dependencies

- `azure-functions` - Azure Functions Python SDK
- `a2a-sdk` - Agent2Agent Protocol SDK
- `requests` - HTTP client (for testing)
- Python 3.9+

See `requirements.txt` for full dependency list.
