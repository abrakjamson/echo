# Echo Server with JSON-RPC Support

A lightweight Azure Functions application that provides HTTP echo and JSON-RPC protocol endpoints.

## Public URL

```
https://echo.azurewebsites.net/api/
```

## Project Structure

```
echo_functions/
├── function_app.py          # Azure Functions app with /echo and /jsonrpc routes
├── jsonrpc_handler.py       # JSON-RPC 1.0 and 2.0 protocol handler
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

**jsonrpc_handler.py**
- `JsonRpcHandler.handle_request(req_body)` - Protocol parser and handler
  - Detects JSON-RPC version (1.0 or 2.0)
  - Validates required fields (method, id)
  - Generates proper error responses
  - Returns echo responses

**test_endpoints.py**
- Local unit tests (handler logic)
- Live HTTP integration tests
- Graceful fallback if endpoints not deployed

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
   - 6 live HTTP integration tests (if endpoints deployed)
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

### Deployment

Deploy to Azure Functions using the Azure CLI or Azure Functions extension:
```bash
func azure functionapp publish <app-name>
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

✅ **Testing**
- 5 local unit tests for handler logic
- 6 HTTP integration tests for deployed endpoints
- All tests passing ✓

## Dependencies

- `azure-functions` - Azure Functions Python SDK
- `requests` - HTTP client (for testing)
- Python 3.9+

See `requirements.txt` for full dependency list.
