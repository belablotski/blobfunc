# Azure Functions: Resilience & Error Handling

Distributed systems fail. Networks blink, storage accounts throttle, and downstream APIs go offline. A production-grade Azure Function must handle these failures gracefully without losing data or entering infinite loops.

---

## 1. Transient Fault Handling
A transient fault is a temporary error, such as a brief network interruption or an HTTP 429 "Too Many Requests" when Azure Storage throttles you for hitting IOPS limits.

*   **SDK Retries:** The `azure-storage-blob` SDK has built-in retry policies enabled by default. It uses **Exponential Backoff** (retrying after 1 second, then 3 seconds, then 7 seconds, etc.). You should tune these parameters (`retry_total`, `retry_backoff_max`) based on your timeout limits.
*   **Never fail immediately** on a network exception. Let the SDK handle the micro-retries.

## 2. Queue Retries and Poison Messages
If a transient error persists beyond the SDK's retries, or if the Python code throws an unhandled exception (e.g., `IndexError` on a malformed CSV), the Function execution fails.

If you are using a **Queue Trigger**:
*   The message is placed back on the queue but remains invisible for a short duration.
*   The function will attempt to process it again (default is 5 total attempts).
*   **Poison Queue:** If the function fails 5 times, the message is permanently moved to a "Poison Queue" (e.g., `myqueue-poison`).
*   **Actionable Advice:** You must set up an alert on the poison queue depth. When messages land there, it means you have a systemic bug or deeply malformed data that requires human intervention.

## 3. Idempotency (Exactly-Once Semantics)
Because queue messages can be retried, your function might execute successfully, crash right *before* it deletes the message from the queue, and then run *again*. Your function must be **Idempotent**—running it twice with the same input must yield the exact same result without corrupting the system.

*   **Overwriting Blobs:** Writing to Blob Storage is inherently idempotent if you overwrite the exact same destination path (`blob_client.upload_blob(overwrite=True)`).
*   **Database Inserts:** If your function inserts rows into a SQL database, running it twice might cause duplicate rows. You must use `UPSERT` (MERGE) logic based on the blob's unique identifier to ensure data is updated, not duplicated, on retries.

## 4. Circuit Breakers
If your function relies on an external API (e.g., an ML model for classification) and that API goes down, continuing to pull messages from the queue and failing 5 times before poisoning them is a waste of resources and clogs your poison queue.
*   Consider implementing a Circuit Breaker pattern (using libraries like `pyfailsafe` or `tenacity`). If the API fails 10 times in a row, the circuit "opens" and the function immediately pauses processing or intentionally throws an error to back off, giving the downstream system time to recover.
