import json


class JsonRpcHandler:
    """Handles JSON-RPC 1.0 and 2.0 protocol requests."""

    @staticmethod
    def handle_request(req_body):
        """
        Parse and handle a JSON-RPC request.
        
        Args:
            req_body: dict parsed from JSON request body
            
        Returns:
            dict: JSON-RPC response object
        """
        try:
            # Determine version based on presence of "jsonrpc" field
            is_v2 = isinstance(req_body, dict) and req_body.get("jsonrpc") == "2.0"
            
            # Validate required fields
            if not isinstance(req_body, dict):
                return JsonRpcHandler._error_response(
                    None, -32700, "Parse error", is_v2
                )
            
            # JSON-RPC 1.0 doesn't require version field, so we accept requests without it
            # JSON-RPC 2.0 requires the "jsonrpc": "2.0" field
            
            if "method" not in req_body:
                return JsonRpcHandler._error_response(
                    req_body.get("id"), -32600, "Invalid Request", is_v2
                )
            
            # Echo back the request in the result
            response = {
                "result": req_body
            }
            
            # Add id if present (required for JSON-RPC 2.0 requests)
            if "id" in req_body:
                response["id"] = req_body["id"]
            
            # Add jsonrpc field if this is a 2.0 request
            if is_v2:
                response["jsonrpc"] = "2.0"
            
            return response
            
        except Exception as e:
            return JsonRpcHandler._error_response(
                req_body.get("id") if isinstance(req_body, dict) else None,
                -32603,
                f"Internal error: {str(e)}",
                is_v2
            )

    @staticmethod
    def _error_response(request_id, error_code, error_message, is_v2):
        """Generate a JSON-RPC error response."""
        response = {
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        if is_v2:
            response["jsonrpc"] = "2.0"
        
        return response
