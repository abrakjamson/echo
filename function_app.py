import azure.functions as func
import json
import logging
from jsonrpc_handler import JsonRpcHandler
from mcp_handler import McpHandler
from a2a_handler import A2AHandler

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Agent Card for A2A Protocol Discovery
AGENT_CARD = {
    "name": "Echo Server",
    "description": "A lightweight echo server supporting multiple protocols: HTTP echo, JSON-RPC 1.0/2.0, MCP, and Agent2Agent (A2A)",
    "version": "1.0.0",
    "agentId": "echo-server",
    "endpoint": "https://echo.azurewebsites.net/api/message:send",
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

    return func.HttpResponse(
        body=json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="message:send", methods=["POST"])
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


@app.route(route=".well-known/agent-card.json", methods=["GET"])
def agent_card(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Agent card requested.')
    
    return func.HttpResponse(
        body=json.dumps(AGENT_CARD),
        status_code=200,
        mimetype="application/json"
    )
