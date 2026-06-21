# Azure Functions: Cost Optimization

Serverless computing is heavily marketed as "pay only for what you use," but poorly optimized architectures can lead to massive, unexpected bills, especially when processing blobs at scale.

---

## 1. Compute Costs: Execution Time vs Memory
In the Azure Functions Consumption Plan, you are billed in **GB-seconds**. This is (Execution Time in seconds) × (Memory Allocated in GB).

*   **Optimize Algorithms:** As discussed previously, upgrading a sorting algorithm from $O(n^2)$ to $O(n \log n)$ can reduce execution time from minutes to milliseconds. This directly cuts your compute bill.
*   **Memory Profiling:** Ensure your function isn't allocating unnecessary memory. Streaming massive blobs instead of loading them into memory not only prevents crashes but lowers the GB-seconds billing metric.

## 2. Storage Transaction Costs (The Hidden Killer)
Storage is cheap; **Transactions are expensive**. Azure bills you for every REST API call made to the Storage Account (e.g., `PutBlob`, `GetBlob`, `ListBlobs`).

*   **The Problem:** If you process 100 million tiny blobs, the compute cost might be $10, but the storage transaction cost (reading the blob, writing the output, deleting the queue message) could be $500.
*   **The Solution:** Batching. If possible, compact small blobs into larger ones before processing. Processing one 100MB blob is exponentially cheaper in transaction costs than processing 10,000 files of 10KB each.
*   **Avoid Polling:** This is why you must not use the classic Blob Trigger or write your own loops that constantly call `list_blobs()`. Event Grid pushes events to you, drastically reducing `LIST` API transaction costs.

## 3. Choosing the Right Hosting Plan
The Consumption Plan is not always the cheapest option at scale.

*   **Consumption Plan:** Best for spiky, unpredictable workloads. You pay per execution. Cold starts occur when scaling from zero.
*   **Flex Consumption Plan** *(GA since 2024 — the recommended default for most new workloads):* A modern evolution of the Consumption Plan with per-instance billing (more predictable than per-execution), **always-ready instances** (eliminating cold starts), built-in **VNet integration**, and scales to zero when idle. It fills the gap between Consumption and Premium without requiring a committed baseline spend.
    *   **When to choose:** You need no cold starts and/or VNet access, but don't want to pay for permanently running Premium instances.
*   **Premium Plan:** You pay a baseline monthly fee for pre-warmed instances, but the per-execution cost above that baseline can be cheaper depending on volume.
    *   **When to switch:** If your function runs constantly (24/7 at high throughput), the Premium Plan (or even a Dedicated App Service Plan) often becomes cheaper.
    *   Premium also supports unlimited timeouts (`"functionTimeout": "-1"`) and is required for features not yet available on Flex Consumption.
*   **Dedicated (App Service) Plan:** Best when you already have reserved App Service capacity or need full control over the underlying compute.

## 4. Log Analytics Data Retention
Application Insights stores telemetry data in a Log Analytics Workspace. You are billed per GB of data ingested.

*   **Optimization:** If you log heavily, your Log Analytics bill will eclipse your compute bill. Implement Adaptive Sampling (as discussed in Observability) and reduce the retention period (e.g., from 90 days to 30 days) for non-critical logs to control storage costs.
