# Azure Functions: Blob Processing Output Methods

When processing blobs in Azure Functions, you must decide how and where to store the results. The right choice depends heavily on your architecture, whether the processing is synchronous or asynchronous, and how the data will be used downstream.

Here is a breakdown of the primary patterns for storing or returning results, including when to use them and their potential pitfalls.

---

## 1. Write to the Same Blob (Modify Input)
You overwrite the original input blob with the processed data.

*   **Best for:** In-place data scrubbing, applying compression, or standardizing formats where keeping the raw original is strictly unnecessary or violates compliance (e.g., scrubbing PII).
*   **The Pitfall (Infinite Loops):** If your function is triggered by a Blob Trigger or Event Grid on `BlobCreated`/`BlobUpdated`, overwriting the blob will instantly re-trigger the function, causing an infinite execution loop.
*   **Risk:** It is destructive. If your processing logic has a bug or crashes halfway through, your original data is lost or corrupted.

## 2. Write to Another Blob (Different Container or Postfix)
You treat the input blob as immutable and write the output to a new destination.

*   **Best for:** Standard ETL pipelines and the "Medallion Architecture" (Bronze -> Silver -> Gold). For example, raw data lands in `raw-container`, your function cleans it and writes to `processed-container`.
*   **The Advantage:** Completely safe. You never lose the raw data. Furthermore, writing to `processed-container` can cleanly trigger the *next* Azure Function in your pipeline without risking infinite loops back to this function (as long as the output container does not have an Event Grid subscription or Blob Trigger pointing to the same function).
*   **Consideration:** Storage costs increase, but Azure Blob Storage is generally cheap enough that data safety outweighs the storage cost.

## 3. Set Blob Metadata
Instead of modifying the file content, you attach key-value string pairs to the blob's metadata (e.g., `{"status": "processed", "rowCount": "1500"}`).

*   **Best for:** Storing contextual data about the file that the application needs when downloading it.
*   **The Advantage:** Extremely fast. You don't have to download or upload the massive file content; you just update the headers via the SDK.
*   **The Pitfall:** **You cannot search by metadata.** If you have a million blobs and want to find all blobs where `"status" == "processed"`, metadata is useless. You would have to download the metadata for all one million blobs to find the right ones.

## 4. Set Blob Index Tags
Similar to metadata, these are key-value pairs attached to the blob, but they are tracked by a secondary index managed by Azure.

*   **Best for:** Categorization, search, and lifecycle management.
*   **The Advantage:** **They are queryable.** You can use Azure's `Find Blobs by Tags` API to execute SQL-like queries (e.g., `@container = 'mycontainer' AND "status" = 'processed'`). You can also configure Azure Lifecycle Management to automatically delete blobs that have a specific index tag.
*   **Consideration:** There is a small cost associated with maintaining the index, and you are limited to 10 tags per blob.

## 5. Return in Function Response
You return the processed data directly in the HTTP response body.

*   **Best for:** Synchronous REST APIs where a UI or a user is waiting for immediate feedback (e.g., an HTTP trigger returning sorted JSON).
*   **The Pitfall:** Completely useless for background processing. If the function is triggered by a Queue or Event Grid, there is no HTTP caller waiting for a response. Additionally, returning gigabytes of data in an HTTP response will likely time out or hit memory limits.

## 6. Call External APIs / Databases
You extract metrics, aggregates, or specific rows and write them to a structured database (like Cosmos DB, Azure SQL) or stream them to Event Hubs.

*   **Best for:** Extracting business value from unstructured blobs. For example, processing a massive CSV of IoT telemetry but only saving the anomaly alerts to a SQL database.
*   **The Advantage:** Separates unstructured raw storage (Blob) from structured, queryable serving layers (Database).

---

## Summary Recommendation
In enterprise serverless architectures, the gold standard is almost always **Method 2 (Write to another container)** combined with **Method 6 (Write metrics to a Database)**. You treat the original blob as read-only, write the clean output to a new blob, and log the success or extracted statistics to a database or event stream.

---

## Example from This Codebase

`sort_blob_function` in `function_app.py` demonstrates Methods 2 and 5 working together:
- When `output_blob` is **omitted**, the sorted data is returned directly in the HTTP response body (**Method 5**).
- When `output_blob` is **provided**, the sorted CSV is written to another blob (**Method 2**) and only a reference (`container` + `blob` name) is returned in the response.