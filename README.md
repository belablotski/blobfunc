# blobfunc

An Azure Functions app (Python v2) that exposes a sorting endpoint via HTTP.

## Project structure

```
function_app.py      # Azure Function HTTP trigger
sort.py              # sort_v1 — selection sort implementation
test_sort.py         # Unit tests for sort_v1
host.json            # Azure Functions host configuration
local.settings.json  # Local development settings
requirements.txt     # Python dependencies
```

## API

### `POST /api/sort`

Sorts a list of numbers in ascending order.

**Request body:**
```json
{ "data": [3, 4, 1, 5] }
```

**Response:**
```json
{ "sorted": [1, 3, 4, 5] }
```

**Auth level:** `FUNCTION` — requires a `code` query parameter or `x-functions-key` header when deployed.

## Running locally

**Prerequisites:** [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) and Python 3.8+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

## Running tests

```bash
python3 -m unittest test_sort -v
```
