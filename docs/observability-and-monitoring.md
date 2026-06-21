# Azure Functions: Observability & Monitoring

When processing millions of blobs across hundreds of concurrent function executions, traditional logging (e.g., `print()` statements) becomes useless. You need structured observability to understand system health and trace failures.

---

## 1. Application Insights & Sampling
Azure Functions natively integrates with **Azure Application Insights**.

**The Pitfall:** If you process 10 million blobs and log 5 lines per blob, you will ingest 50 million log lines into App Insights. This will cost a massive amount of money and make querying incredibly slow.

**The Solution: Sampling**
You must configure telemetry sampling in your `host.json` file.
*   **Adaptive Sampling:** The host automatically adjusts the sampling rate based on traffic volume. During a spike, it might only send 5% of successful requests to App Insights, but it attempts to send 100% of exceptions.
*   Configure this carefully to ensure you capture failures without paying for gigabytes of "File processed successfully" logs.

## 2. Distributed Tracing
If your architecture is Event Grid -> Queue -> Function -> Storage, tracking a single file's journey requires Distributed Tracing.

*   Azure uses the **W3C Trace Context** standard.
*   When Event Grid fires, it generates a `traceparent` ID. This ID is passed into the Queue message and automatically picked up by the Azure Functions Python worker.
*   In Application Insights, you can use the "Application Map" or "End-to-end transaction details" to see the exact flow. If a file fails, you can see if the failure happened at the Event Grid level, the Queue level, or inside your Python code, all linked by a single Operation ID.

## 3. Custom Metrics
Logs are for debugging; metrics are for alerting. Instead of logging "Processed 1500 rows" as text, you should emit custom metrics.

*   Use the OpenTelemetry SDK (or the older App Insights SDK) to emit metrics like:
    *   `RowsProcessed` (Counter)
    *   `ProcessingDurationMs` (Histogram)
    *   `InvalidFilesDetected` (Counter)
*   **Alerting:** You can then set up Azure Monitor Alerts. For example: "Fire a High Severity alert if the `InvalidFilesDetected` metric exceeds 50 in a 5-minute window." This is much cheaper and faster than writing log-analytics queries to count text occurrences.
