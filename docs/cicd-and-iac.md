# Azure Functions: CI/CD and Infrastructure as Code

Manually clicking through the Azure Portal to create storage accounts and deploy Python code is acceptable for prototypes, but forbidden in production. You need automated, repeatable deployments.

---

## 1. Infrastructure as Code (IaC)
Your infrastructure (Function App, Storage Accounts, Queues, Event Grid, RBAC role assignments) must be defined in code and version-controlled.

*   **Bicep or Terraform:** Choose either Azure Bicep (Microsoft's native IaC language) or HashiCorp Terraform.
*   **Benefits:**
    *   **Consistency:** You can stamp out identical `dev`, `staging`, and `prod` environments in minutes.
    *   **Disaster Recovery:** If someone accidentally deletes the resource group, you can recreate the entire architecture with a single command.
    *   **Auditability:** Every change to the infrastructure is reviewed via a Pull Request.

## 2. CI/CD Pipelines
Code should be automatically tested and deployed when merged to the main branch.

*   **GitHub Actions or Azure DevOps:**
    1.  **Continuous Integration (CI):** On every Pull Request, the pipeline runs `flake8` (linting), `mypy` (type checking), and `pytest` (unit tests). If any fail, the PR is blocked.
    2.  **Continuous Deployment (CD):** On merge to `main`, the pipeline uses the Azure CLI or Azure Functions Action to package the Python code into a `.zip` file and publish it to the Function App.

## 3. Deployment Slots (Zero Downtime)
When you deploy a new version of your Python code, the Function App restarts. If you are actively processing thousands of queue messages, a restart can interrupt inflight executions, causing them to fail and retry.

**The Solution: Deployment Slots**
*   Create a `staging` slot on your Function App.
*   Your CI/CD pipeline deploys the new code to the `staging` slot. The `production` slot continues processing the queue without interruption.
*   Once the `staging` slot is fully warmed up and health checks pass, you execute a **Swap** command.
*   Azure swaps the network routing instantly. The staging slot becomes production, and the old production slot becomes staging. This guarantees zero downtime and zero dropped messages during updates.
