# Azure Functions: Blob Processing Input & Orchestration Methods

When processing a large number of existing blobs or handling a continuous stream of new ones, you need an architectural strategy to iterate through the files and trigger your Azure Functions. These methods broadly fall into two categories: **Event-Driven** (reacting to new files) and **Batch/Scheduled** (iterating over existing files).

Here is a breakdown of the primary input and orchestration methods, including when to use them and their pros and cons.

---

## 1. Azure Event Grid + Queue Storage (The Gold Standard for New Files)
Instead of iterating, you react. When a new blob lands in the storage account, Azure Storage fires an event to Event Grid.

*   **How it works:** Event Grid routes the "BlobCreated" event to an Azure Storage Queue (or Service Bus). Your Azure Function uses a **Queue Trigger** to consume the messages and process the corresponding blobs.
*   **Best for:** Real-time processing of new files as they arrive at scale.
*   **Pros:** Highly scalable, decoupled, built-in dead-lettering, and excellent concurrency control (you can configure `host.json` to limit how many files a single Python worker processes at once).
*   **Cons:** Only works for *new* files. It doesn't help you process a backlog of existing files sitting in a container.

    > **Backfill pattern:** To process existing blobs with the same pipeline, list them with the SDK (`container_client.list_blobs()`) and manually enqueue each blob path into the same Queue. The Queue-triggered function then handles both historical and new files uniformly — no second code path needed.

## 2. Azure Data Factory / Synapse Pipelines (The Visual Orchestrator)
ADF is Azure's premier ETL service. You can build a pipeline that explicitly iterates through a blob container.

*   **How it works:** You use a `Get Metadata` activity to list the blobs in a container, pass the output to a `ForEach` activity, and inside the loop, you use an `Azure Function` activity to call your HTTP-triggered function for each blob. Alternatively, you can have ADF drop messages into a Queue.
*   **Best for:** Processing massive backlogs of existing files, or complex workflows where the function is just one step in a larger ETL process.
*   **Pros:** Visual orchestration, excellent retry policies, and you can easily control the batch size and parallel execution limits.
*   **Cons:** Adds a new service (and cost) to your architecture. Calling an HTTP function millions of times directly from ADF can also be slower than using Queue triggers.

## 3. The Classic "Blob Trigger" (The Anti-Pattern at Scale)
You put a `@app.blob_trigger` directly on your Python function.

*   **How it works:** The Azure Functions host continually scans the storage account logs to see if new blobs have been added and triggers your code.
*   **Best for:** Very small, low-traffic applications (e.g., a few dozen files a day).
*   **Pros:** Easiest to set up. Zero external configuration required.
*   **Cons:** **Do not use this at scale.** Polling storage logs is notoriously slow and unreliable. It can suffer from massive latency (sometimes taking 10+ minutes to notice a new file) and can easily drop events if the traffic spikes. *(Note: The modern blob trigger supports an Event Grid source under the hood, but Queue Storage is still preferred for resilience).*

## 4. Timer Trigger + SDK Iteration (The DIY Batch Processor)
You write a function triggered by a schedule (e.g., `@app.timer_trigger(schedule="0 0 * * * *")` for every hour).

*   **How it works:** The function wakes up, uses the `BlobServiceClient` to list the blobs in a container (`container_client.list_blobs()`), and processes them in a `for` loop.
*   **Best for:** Nightly batch jobs on a small-to-medium number of files.
*   **Pros:** Simple, self-contained entirely within the Function App.
*   **Cons:**
    *   **The 10-Minute Limit:** If you have 100,000 files, the function will hit the Consumption Plan timeout before the loop finishes.
    *   **No Parallelism:** It processes files sequentially on a single thread.
    *   *Fix:* To make this scale, the Timer function should only *list* the blobs and push their paths into a Queue, letting a separate Queue-triggered function do the actual parallel processing (the "Fan-Out" pattern). At that point you've essentially built Method 1 manually — which is why Event Grid is preferred when files arrive continuously.

## 5. Durable Functions (The Code-First Orchestrator)
Durable Functions allow you to write stateful workflows in Python without needing external services like Data Factory.

*   **How it works:** You write an "Orchestrator" function. It uses the SDK to list all blobs in the container. It then uses the `context.call_activity` method to fan-out and trigger hundreds of parallel "Activity" functions, passing each one a specific blob to process.
*   **Best for:** Complex, code-driven orchestration of existing backlogs where you want to stay entirely within the Azure Functions ecosystem.
*   **Pros:** Bypasses the 10-minute timeout (Orchestrators can run forever), provides native fan-out/fan-in parallelism, and offers excellent error handling.
*   **Cons:** Has a steeper learning curve and requires slightly more complex state management compared to standard functions.

---

## Summary Recommendation

*   **If you are processing files continuously as they arrive:** Use **Method 1 (Event Grid + Queue Storage)**.
*   **If you need to process a massive existing backlog of millions of files:** Use **Method 2 (Azure Data Factory)** to drop messages into a Queue, or write a **Method 5 (Durable Function Orchestrator)** to fan-out the workload.

---

## See Also

*   [bindings-vs-sdk.md](bindings-vs-sdk.md) — once a blob is triggered, how to read its content (bindings vs. `BlobServiceClient`)
*   [output-methods.md](output-methods.md) — where and how to store the processing result