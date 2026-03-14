import azure.functions as func
import logging

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