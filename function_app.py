import azure.functions as func
import json
import logging
from jsonrpc_handler import JsonRpcHandler
from mcp_handler import McpHandler
from a2a_handler import A2AHandler
from a2a_jsonrpc_handler import A2AJsonRpcHandler

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Agent Card for A2A Protocol Discovery
AGENT_CARD = {
    "name": "Echo Server",
    "description": "A lightweight echo server supporting multiple protocols: HTTP echo, JSON-RPC 1.0/2.0, MCP, and Agent2Agent (A2A) via both HTTP/REST and JSON-RPC bindings",
    "version": "1.0.0",
    "agentId": "echo-server",
    "endpoint": "https://echo.azurewebsites.net/api/a2a/message:send",
    "protocolVersion": "1.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "extendedAgentCard": False
    },
    "security": [],
    "securitySchemes": {},
    "skills": [
        {
            "name": "echo",
            "description": "Echoes back the input data provided in A2A messages"
        }
    ]
}

@app.route(route="echo")
def depth(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    value = req.params.get('value')
    if not value:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            value = req_body.get('value')

    if value:
        return func.HttpResponse(f"{value}",
                                 status_code=200)
    else:
        return func.HttpResponse(
             "The 'value' field is required.",
             status_code=400
        )
@app.route(route="jsonrpc", methods=["POST"])
def jsonrpc(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('JSON-RPC handler processed a request.')
    
    try:
        req_body = req.get_json()
    except ValueError:
        error_response = {
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )
    
    # Handle the JSON-RPC request
    response = JsonRpcHandler.handle_request(req_body)
    
    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="mcp", methods=["POST"])
def mcp(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MCP handler processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        error_response = {"error": {"code": -32700, "message": "Parse error"}}
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )

    response = McpHandler.handle_request(req_body)

    # Handle JSON-RPC notifications (no response per spec)
    if response is None:
        return func.HttpResponse(status_code=202)

    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="mcp/sse", methods=["POST"])
def mcp_sse(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MCP SSE handler processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "The request body must be valid JSON.",
            status_code=400
        )

    response = McpHandler.handle_request(req_body)

    # Handle JSON-RPC notifications
    if response is None:
        return func.HttpResponse(status_code=202)

    # Format as MCP SSE message event
    sse_data = f"event: message\ndata: {json.dumps(response)}\n\n"

    return func.HttpResponse(
        body=sse_data,
        status_code=200,
        mimetype="text/event-stream"
    )


@app.route(route="a2a/message:send", methods=["POST"])
def send_message(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A2A SendMessage handler processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        error_response = {
            "error": {
                "code": "parse_error",
                "message": "Invalid JSON"
            }
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )

    response = A2AHandler.handle_request(req_body)

    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="a2a/tasks/{task_id}", methods=["GET"])
def get_task(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A2A GetTask handler processed a request.')
    
    task_id = req.route_params.get('task_id')
    
    if not task_id:
        error_response = {
            "error": {
                "code": "invalid_request",
                "message": "Task ID is required"
            }
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )
    
    response = A2AHandler.get_task(task_id)
    
    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="a2a/tasks", methods=["GET"])
def list_tasks(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A2A ListTasks handler processed a request.')
    
    response = A2AHandler.list_tasks()
    
    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="a2a/tasks/{task_id}:cancel", methods=["POST"])
def cancel_task(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A2A CancelTask handler processed a request.')
    
    task_id = req.route_params.get('task_id')
    
    if not task_id:
        error_response = {
            "error": {
                "code": "invalid_request",
                "message": "Task ID is required"
            }
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )
    
    response = A2AHandler.cancel_task(task_id)
    
    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )



@app.route(route="a2a", methods=["POST"])
def a2a_jsonrpc(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('A2A JSON-RPC handler processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=400,
            mimetype="application/json"
        )

    response = A2AJsonRpcHandler.handle_request(req_body)

    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route=".well-known/agent-card.json", methods=["GET"])
def agent_card(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Agent card requested.')
    
    return func.HttpResponse(
        body=json.dumps(AGENT_CARD),
        status_code=200,
        mimetype="application/json"
    )
