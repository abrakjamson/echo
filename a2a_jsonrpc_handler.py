"""A2A Protocol operations via JSON-RPC 2.0 binding."""

import json
import uuid
from a2a.types import Message, TextPart, Role


class A2AJsonRpcHandler:
    """
    Handles A2A Protocol operations via JSON-RPC 2.0 binding.
    
    Maps JSON-RPC method calls to A2A operations:
    - a2a.SendMessage: Send a message and get a response
    - a2a.GetTask: Get task state (stub for echo server)
    - a2a.ListTasks: List tasks (stub for echo server)
    - a2a.CancelTask: Cancel a task (stub for echo server)
    """

    @staticmethod
    def handle_request(req_body):
        """
        Process a JSON-RPC 2.0 request for A2A operations.
        
        Args:
            req_body: Parsed JSON request body (expects JSON-RPC 2.0 format)
            
        Returns:
            Dictionary with JSON-RPC 2.0 response
        """
        # Validate that req_body is a dictionary
        if not isinstance(req_body, dict):
            return A2AJsonRpcHandler._error_response(
                None, -32700, "Parse error", True
            )
        
        # Extract fields
        jsonrpc_version = req_body.get("jsonrpc")
        method = req_body.get("method")
        params = req_body.get("params", {})
        request_id = req_body.get("id")
        
        # Validate JSON-RPC 2.0
        if jsonrpc_version != "2.0":
            return A2AJsonRpcHandler._error_response(
                request_id, -32600, "Invalid Request: jsonrpc field must be '2.0'", True
            )
        
        # Validate method field
        if not method:
            return A2AJsonRpcHandler._error_response(
                request_id, -32600, "Invalid Request: method field required", True
            )
        
        # Route to appropriate A2A operation
        try:
            if method == "a2a.SendMessage":
                result = A2AJsonRpcHandler._send_message(params)
            elif method == "a2a.GetTask":
                result = A2AJsonRpcHandler._get_task(params)
            elif method == "a2a.ListTasks":
                result = A2AJsonRpcHandler._list_tasks(params)
            elif method == "a2a.CancelTask":
                result = A2AJsonRpcHandler._cancel_task(params)
            else:
                return A2AJsonRpcHandler._error_response(
                    request_id, -32601, f"Method not found: {method}", True
                )
            
            # Build response
            response = {
                "jsonrpc": "2.0",
                "result": result
            }
            
            # Only include id if present in request
            if request_id is not None:
                response["id"] = request_id
            
            return response
            
        except Exception as e:
            return A2AJsonRpcHandler._error_response(
                request_id, -32603, f"Internal error: {str(e)}", True
            )

    @staticmethod
    def _send_message(params):
        """
        A2A SendMessage operation via JSON-RPC.
        
        Expects params to contain an A2A Message object.
        Echoes back a response message with the same content.
        
        Args:
            params: Dictionary with 'message' field containing A2A Message
            
        Returns:
            Dictionary with 'task' or 'message' field containing response
        """
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")
        
        # Extract message from params
        message_data = params.get("message")
        if not message_data:
            raise ValueError("params.message is required for a2a.SendMessage")
        
        # Parse the incoming Message using a2a SDK
        if isinstance(message_data, dict):
            incoming_message = Message.model_validate(message_data)
        else:
            raise ValueError("message must be a JSON object")
        
        # Extract text content from the incoming message
        message_content = ""
        if incoming_message.parts:
            for part in incoming_message.parts:
                inner_part = part.root if hasattr(part, "root") else part
                if hasattr(inner_part, "text"):
                    message_content = inner_part.text
                    break
        
        # Create response message
        parts = [TextPart(text=message_content)] if message_content else [TextPart(text="Echo received")]
        response_message = Message(
            messageId=str(uuid.uuid4()),
            role=Role.agent,
            parts=parts,
            metadata=incoming_message.metadata if incoming_message.metadata else {}
        )
        
        # For echo server, return direct message response (not a task)
        return {
            "message": response_message.model_dump(exclude_none=True, by_alias=True)
        }

    @staticmethod
    def _get_task(params):
        """
        A2A GetTask operation via JSON-RPC (stub for echo server).
        
        Args:
            params: Dictionary with 'id' field for task ID
            
        Returns:
            Dictionary with task information
        """
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")
        
        task_id = params.get("id")
        if not task_id:
            raise ValueError("params.id is required for a2a.GetTask")
        
        # For echo server: return a stub task
        return {
            "task": {
                "id": task_id,
                "status": "completed",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }

    @staticmethod
    def _list_tasks(params):
        """
        A2A ListTasks operation via JSON-RPC (stub for echo server).
        
        Args:
            params: Dictionary with optional filters
            
        Returns:
            Dictionary with list of tasks
        """
        # For echo server: return empty list
        return {
            "tasks": [],
            "nextPageToken": "",
            "pageSize": 0,
            "totalSize": 0
        }

    @staticmethod
    def _cancel_task(params):
        """
        A2A CancelTask operation via JSON-RPC (stub for echo server).
        
        Args:
            params: Dictionary with 'id' field for task ID
            
        Returns:
            Dictionary with updated task information
        """
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")
        
        task_id = params.get("id")
        if not task_id:
            raise ValueError("params.id is required for a2a.CancelTask")
        
        # For echo server: return stub response
        return {
            "task": {
                "id": task_id,
                "status": "canceled",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }

    @staticmethod
    def _error_response(request_id, error_code, error_message, is_v2):
        """Generate a JSON-RPC 2.0 error response."""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        return response
