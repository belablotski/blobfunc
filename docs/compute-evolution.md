# Azure Functions: Compute Evolution (The Exit Strategy)

Azure Functions are an excellent starting point for event-driven workloads. However, as organizations scale, they often encounter hard limits on memory, execution time, or language dependencies. A robust architecture always has an exit strategy to move compute to heavier platforms without breaking the event-driven design.

---

## 1. When to Evolve
You should consider migrating away from Azure Functions when:
*   **Memory Bound:** Your blobs are so large that even chunked streaming is insufficient, and you need 16GB+ of RAM to hold massive pandas DataFrames.
*   **Time Bound:** Processing a single blob takes longer than the 60-minute maximum timeout of the Premium Plan.
*   **Dependency Bound:** You need complex native C++ libraries, specialized ML drivers (CUDA), or legacy OS tools that cannot be packaged cleanly in a Function App.

## 2. Azure Container Apps (ACA)
The easiest evolution path from Azure Functions is **Azure Container Apps**.

*   **What it is:** A fully managed serverless container service built on Kubernetes.
*   **The Transition:** You wrap your Python processing logic in a standard Docker container.
*   **KEDA Integration:** ACA natively supports **KEDA** (Kubernetes Event-driven Autoscaling). KEDA allows your container to scale from zero to hundreds of instances based on the exact same Azure Storage Queue that triggered your Azure Function.
*   **The Result:** You maintain the exact same Event Grid -> Queue architecture, but swap the lightweight Azure Function compute for a heavy-duty Docker container with custom memory/CPU profiles and no strict timeouts.

## 3. Azure Kubernetes Service (AKS)
If your organization already has a massive Kubernetes footprint, maintaining isolated Azure Function Apps might fragment your infrastructure.

*   **The Transition:** Deploy your containerized worker to AKS.
*   **Event-Driven in K8s:** Install KEDA in your AKS cluster. It will monitor your Azure Storage Queue and dynamically spin up Pods to process the blobs, acting exactly like the Azure Functions scale controller but entirely within your K8s environment.

## 4. Azure Batch / Databricks
As discussed in the Ultra-Large files architecture, when compute shifts from "event processing" to "Big Data ETL," the compute should move to specialized clusters.

*   **The Strategy:** Keep a very lightweight Azure Function attached to the Queue. Its only job is to read the blob path and make an API call to Databricks (starting a Spark job) or Azure Batch (spawning a high-performance compute node). 
*   This keeps the event routing serverless but offloads the heavy lifting to Big Data platforms.
