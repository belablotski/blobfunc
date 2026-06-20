# blobfunc

An Azure Functions app (Python v2) that exposes two HTTP sorting endpoints:

- `POST /api/sort` — sorts a JSON array in-place
- `GET /api/sort-blob` — reads a CSV blob from Azure Storage, sorts rows by the integer identifier in the first column, and returns the result

## Project structure

```
function_app.py      # Azure Function HTTP triggers
sort.py              # sort_v1 — selection sort implementation
test_sort.py         # Unit tests for sort_v1
host.json            # Azure Functions host configuration
local.settings.json  # Local development settings (not committed)
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
{ "sorted": [1, 3, 4, 5], "duration_ms": 0.0021 }
```

---

### `GET /api/sort-blob?container=<container>&blob=<blob>`

Reads a CSV blob from Azure Storage, sorts data rows by the first column (integer identifier), and returns the result.

**Query parameters:**

| Parameter          | Description                                                         |
|---------------------|---------------------------------------------------------------------|
| `container`         | Storage container name                                              |
| `blob`              | Blob name (e.g. `data.csv`)                                         |
| `output_blob`       | *(optional)* Blob name to write the sorted CSV into                 |
| `output_container`  | *(optional)* Container for the output blob (defaults to `container`)|

> **Line endings:** when writing the sorted output blob, the CSV is produced with `\r\n` line terminators per [RFC 4180](https://www.ietf.org/rfc/rfc4180.txt). Input blobs with `\n`-only endings are accepted and parsed correctly.

**Example CSV blob (`data.csv`):**
```
id,name,value
3,alice,100
1,bob,200
2,carol,300
```

**Response (JSON only):**
```json
{
  "header": ["id", "name", "value"],
  "rows": [["1","bob","200"], ["2","carol","300"], ["3","alice","100"]],
  "duration_ms": 0.0012
}
```

**Response (with `output_blob`):**
```json
{
  "output": { "container": "mycontainer", "blob": "sorted.csv" },
  "duration_ms": 0.0012
}
```

**Auth level:** `FUNCTION` — requires a `code` query parameter or `x-functions-key` header when deployed to Azure.

---

## Local end-to-end workflow

### Prerequisites

- Python 3.8+
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) (`func`)
- Node.js (for Azurite)

### 1. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Azurite (local storage emulator)

In a dedicated terminal:

```bash
npx azurite --location .azurite --debug .azurite/debug.log --skipApiVersionCheck
```

> `--skipApiVersionCheck` is required because the `azure-storage-blob` SDK may use an API version newer than the locally installed Azurite.

Azurite listens on:
- Blob service: `http://127.0.0.1:10000`
- Queue service: `http://127.0.0.1:10001`
- Table service: `http://127.0.0.1:10002`

### 3. Create a container and upload a test CSV

```bash
az storage container create --name mycontainer \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

echo "id,name,value
3,alice,100
1,bob,200
2,carol,300" > /tmp/data.csv

az storage blob upload --container-name mycontainer --name data.csv --file /tmp/data.csv \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
```

### 4. Start the function app

In another terminal:

```bash
func start
```

### 5. Test the endpoints

**Sort a JSON array:**
```bash
curl -X POST http://localhost:7071/api/sort \
  -H "Content-Type: application/json" \
  -d '{"data": [3, 4, 1, 5]}'
```

**Sort a CSV blob (return JSON only):**
```bash
curl "http://localhost:7071/api/sort-blob?container=mycontainer&blob=data.csv"
```

**Sort and save the result to another blob:**
```bash
curl "http://localhost:7071/api/sort-blob?container=mycontainer&blob=data.csv&output_blob=sorted.csv"
```

---

## Running tests

```bash
python3 -m unittest test_sort -v
```

