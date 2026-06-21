# Azure Functions: High Availability (HA) & Disaster Recovery (DR)

When an architecture scales to enterprise production, you must plan for regional outages. Azure regions are highly reliable, but natural disasters or major platform incidents can take an entire region (e.g., East US) offline.

---

## 1. Geo-Redundant Storage
By default, Azure Storage is Locally Redundant (LRS), meaning data is replicated three times within a single data center.
*   **For DR:** Upgrade your Storage Accounts to **Read-Access Geo-Redundant Storage (RA-GRS)**.
*   **How it works:** Data written to the primary region is asynchronously replicated to a paired secondary region (e.g., East US replicates to West US). If the primary region fails, you can still read your data from the secondary region.

## 2. Multi-Region Active-Passive Architecture
An Azure Function App lives in a single region. If that region goes down, your code stops running.

*   **The Setup:** Deploy identical Function Apps and Storage Queues to both Region A (Primary) and Region B (Passive).
*   **Failover Routing:** Use **Azure Traffic Manager** or **Azure Front Door** for HTTP triggers to route traffic. For Event Grid, you can configure multiple endpoints or use custom routing logic to push events to Region B if Region A is unresponsive.
*   **Execution:** Under normal conditions, only Region A processes blobs. If Region A goes down, traffic is routed to Region B, which begins processing the RA-GRS replicated blobs.

## 3. RTO and RPO
You must define business objectives for failures:
*   **RPO (Recovery Point Objective):** How much data can you afford to lose? Because RA-GRS replication is asynchronous, a sudden regional failure might result in a few minutes of lost data (data written to Region A but not yet copied to Region B).
*   **RTO (Recovery Time Objective):** How quickly must the system be back online? An Active-Active architecture has an RTO of near zero, but an Active-Passive architecture where you must manually trigger a failover script might have an RTO of hours.

## 4. Disaster Recovery Drills
An untested DR plan is not a DR plan. You must regularly conduct failover drills to ensure your infrastructure as code (IaC) can spin up secondary environments and that your data replication is functioning as expected.
