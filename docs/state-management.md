# Azure Functions: State Management and Deduplication

Azure Functions, by design, are **stateless**. Every execution is isolated. However, business requirements often demand stateful processing (knowing about past files or aggregating data across multiple files).

---

## 1. Global Deduplication
In an event-driven system, events can sometimes be delivered twice (At-Least-Once delivery). Furthermore, users might accidentally upload the exact same file twice.

*   **The Problem:** If you process `sales-data.csv` twice, you double-count revenue.
*   **The Solution (Stateful Check):** Before processing a blob, the function calculates a hash of the file (or uses a unique ID in the filename) and checks an external fast-lookup store (like **Azure Redis Cache** or **Cosmos DB**).
*   **Execution:** 
    1. Check Redis for `hash:12345`.
    2. If it exists, skip processing.
    3. If not, write a lock to Redis, process the file, and update the Redis key with the final status.

## 2. Cross-Blob Aggregation
What if you receive 1,000 tiny blobs containing daily sales, and you need to generate a single monthly report blob?

*   **The Anti-Pattern:** A single function triggers on a timer, downloads all 1,000 blobs, sums them in memory, and writes the output. This hits timeout and memory limits.
*   **The Solution (Durable Entities):** Use **Azure Durable Functions Entities**. Entities are stateful actors that manage their own state.
*   **Execution:** 
    1. A Queue Trigger fires for each individual daily blob.
    2. The function reads the single blob and sends a "Add Sales" message to the Durable Entity.
    3. The Entity keeps a running total in its state.
    4. At the end of the month, a Timer Function triggers the Entity to write its final aggregated state to the monthly report blob.

## 3. Concurrency and Race Conditions
When hundreds of Python workers execute simultaneously, they will invariably attempt to update the same records or create the same output folders.

*   **Blob Leases:** Use Azure Storage Blob Leases to implement distributed locks. A function acquires a lease on a blob (locking it for 15-60 seconds). If another worker tries to modify the blob, it receives an error and backs off.
*   **ETags:** Use Optimistic Concurrency via ETags. Read the blob, get its ETag, modify the data, and send the write request with an `If-Match: <ETag>` header. If another worker changed the blob in the meantime, the ETag won't match, the write fails, and your function retries.
