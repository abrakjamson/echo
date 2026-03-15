import json


class McpHandler:
    """MCP handler conforming to JSON-RPC 2.0 specification.

    Behavior:
    - Returns a valid JSON-RPC 2.0 response with "jsonrpc": "2.0".
    - If request is a notification (no "id"), returns None (no response).
    - If request is invalid (not a dict), returns a standard JSON-RPC error.
    - For successful requests, echoes the method and params in the "result" field.
    """

    @staticmethod
    def handle_request(req_body):
        # Validate JSON-RPC structure
        if not isinstance(req_body, dict):
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            }

        request_id = req_body.get("id")
        method = req_body.get("method")
        
        # 1. Handle Notifications (no id) -> No response per JSON-RPC 2.0
        if request_id is None:
            return None

        # 2. Validate Method
        if not method:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request: method field required"},
                "id": request_id
            }

        # 3. Process MCP methods (Echo logic for this server)
        try:
            # Standard echo behavior for any method
            # We echo back the method and its params
            result = {
                "method": method,
                "params": req_body.get("params", {})
            }
            
            # MCP lifecycle special cases (optional for simple echo, but good for compliance)
            if method == "initialize":
                result["protocolVersion"] = "2024-11-05"
                result["capabilities"] = {}
                result["serverInfo"] = {"name": "echo-server", "version": "1.0.0"}

            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": request_id
            }
