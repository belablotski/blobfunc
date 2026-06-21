# Azure Functions: Security & Identity

When moving an Azure Function that processes blobs to production, you must adopt a **Zero Trust** security model. This means eliminating hardcoded secrets, strictly defining permissions, and locking down network access.

---

## 1. Managed Identities (Passwordless Authentication)
The most critical security upgrade is removing connection strings entirely. Connection strings contain Account Keys, which provide full administrative access to the storage account. If leaked, your entire data lake is compromised.

**The Solution:** Use **Azure Managed Identities**.
*   **System-Assigned Identity:** Enable this on your Function App. Azure automatically creates an identity for your app in Azure Active Directory (Entra ID) and manages the credentials invisibly.
*   **Code Impact:** You no longer use `from_connection_string`. Instead, you use the `DefaultAzureCredential` from the `azure-identity` package, which automatically picks up the Managed Identity in the cloud.
*   **Bindings Impact:** If using bindings, you simply set the connection setting to `<ConnectionName>__accountName` (e.g., `BLOB_CONNECTION__accountName="mystorageaccount"`) and the Azure Functions host handles the token acquisition.

## 2. Role-Based Access Control (RBAC)
Once your function has an identity, you must assign it the **Principle of Least Privilege**. Never use the "Contributor" role for data access.

Instead, assign specific data-plane roles on the Storage Account (or even scoped down to the specific container):
*   **Input Container:** Assign `Storage Blob Data Reader`.
*   **Output Container:** Assign `Storage Blob Data Contributor` (allows writing).
*   **Queue Trigger:** Assign `Storage Queue Data Message Processor`.

If your function is compromised, the attacker can only read from the specific input container and write to the output container. They cannot delete the storage account or access other containers.

## 3. Network Security
By default, Azure Storage accounts are accessible via the public internet. In a secure enterprise environment, you must block public access.

*   **VNet Integration:** Place your Azure Function inside an Azure Virtual Network (VNet). Note: This requires the Premium Plan or Dedicated App Service Plan; the basic Consumption plan does not support outbound VNet integration.
*   **Private Endpoints:** Configure a Private Endpoint on your Azure Storage account. This projects the storage account into your VNet with a private IP address (e.g., `10.0.1.5`).
*   **The Result:** Your Azure Function communicates with Blob Storage entirely over the Microsoft backbone network. You can then configure the Storage Account firewall to "Deny all public network access." This completely immunizes your data against internet-based attacks.
