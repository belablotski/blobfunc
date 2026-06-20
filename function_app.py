import csv
import io
import json
import os
import time

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

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


@app.route(route="sort-blob")
def sort_blob_function(req: func.HttpRequest) -> func.HttpResponse:
    container = req.params.get("container")
    blob_name = req.params.get("blob")

    if not container or not blob_name:
        return func.HttpResponse(
            json.dumps({"error": "Query parameters 'container' and 'blob' are required"}),
            status_code=400,
            mimetype="application/json",
        )

    conn_str = os.environ.get("BLOB_CONNECTION_STRING")
    if not conn_str:
        return func.HttpResponse(
            json.dumps({"error": "BLOB_CONNECTION_STRING is not configured"}),
            status_code=500,
            mimetype="application/json",
        )

    try:
        blob_client = BlobServiceClient.from_connection_string(conn_str).get_blob_client(
            container=container, blob=blob_name
        )
        content = blob_client.download_blob().readall().decode("utf-8")
    except ResourceNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": f"Blob '{blob_name}' not found in container '{container}'"}),
            status_code=404,
            mimetype="application/json",
        )

    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if len(rows) < 1:
        return func.HttpResponse(
            json.dumps({"error": "Blob is empty"}),
            status_code=422,
            mimetype="application/json",
        )

    header = rows[0]
    data_rows = rows[1:]

    try:
        start = time.perf_counter()
        data_rows.sort(key=lambda row: int(row[0]))
        duration_ms = (time.perf_counter() - start) * 1000
    except (ValueError, IndexError):
        return func.HttpResponse(
            json.dumps({"error": "First column must be an integer identifier in every data row"}),
            status_code=422,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({
            "header": header,
            "rows": data_rows,
            "duration_ms": round(duration_ms, 4),
        }),
        status_code=200,
        mimetype="application/json",
    )
