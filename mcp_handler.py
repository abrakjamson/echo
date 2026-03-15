import json


class McpHandler:
    """Simple MCP handler that echoes any JSON request under the 'result' field.

    Behavior:
    - If request body is not a dict, return a parse error (code -32700).
    - Otherwise return {"result": <original_request>} and include "id" if provided.
    """

    @staticmethod
    def handle_request(req_body):
        try:
            if not isinstance(req_body, dict):
                return {"error": {"code": -32700, "message": "Parse error"}}

            response = {"result": req_body}
            if "id" in req_body:
                response["id"] = req_body["id"]

            return response

        except Exception as e:
            return {
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": req_body.get("id") if isinstance(req_body, dict) else None,
            }
