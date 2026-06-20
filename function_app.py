import azure.functions as func
import json
import time

from sort import sort_v1

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="sort")
def sort_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Request body must be valid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    if "data" not in body or not isinstance(body["data"], list):
        return func.HttpResponse(
            json.dumps({"error": "Request body must contain a 'data' array"}),
            status_code=400,
            mimetype="application/json",
        )

    data = body["data"]
    start = time.perf_counter()
    sort_v1(data)
    duration_ms = (time.perf_counter() - start) * 1000
    return func.HttpResponse(
        json.dumps({"sorted": data, "duration_ms": round(duration_ms, 4)}),
        status_code=200,
        mimetype="application/json",
    )
