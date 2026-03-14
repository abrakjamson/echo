import azure.functions as func
import json
import logging
from jsonrpc_handler import JsonRpcHandler

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

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
