# Document Translation Service on Azure Functions

[![Azure Functions Deployment](https://github.com/PlumyCat/Translation__MCP_func-v1/actions/workflows/azure-functions-deploy.yml/badge.svg?branch=main)](https://github.com/PlumyCat/Translation__MCP_func-v1/actions/workflows/azure-functions-deploy.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project migrates a **document translation service** from an **Azure Container App** to an **Azure Functions** app. The goal is to significantly **reduce hosting costs** while maintaining the full functionality of the original service. Clients can continue using the same API endpoints with no change in integration. The solution offers **faster scaling**, simplified maintenance, and **usage-based billing**.

---

## ✨ Features

* 💰 **Cost Reduction** – From always-on containers to on-demand execution with Azure Functions Consumption Plan. Pay only for execution time, with potential savings of *60% to 80%*.
* ✅ **Same Features** – Keeps all functionalities from the original service:

  * Translate documents using Azure Translator
  * Supports multiple file formats (PDF, DOCX, TXT, etc.)
  * Optional OneDrive integration for file upload/download
  * Translation status tracking and result retrieval
  * Backward-compatible API structure for clients
* 🚀 **Auto-Scaling Performance** – Serverless architecture scales up and down automatically based on demand.
* 📊 **Improved Monitoring** – Native Application Insights integration for logs, metrics, performance, and error tracing.
* 🔒 **Security Built-in** – Protects endpoints with Function-level keys, allows Azure AD auth, and securely manages Translator/Storage credentials.

---

## 🛠️ Requirements

Before deploying or running the project:

* Active Azure Subscription
* [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
* [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
* Python 3.9+
* PowerShell (for the deployment script)

You also need:

* Azure Translator resource or Cognitive Services API Key
* Azure Storage Account

---

## 🚀 Local Installation

```bash
git clone https://github.com/PlumyCat/Translation__MCP_func-v1.git
cd Translation__MCP_func-v1
pip install -r requirements.txt
```

Then copy `local.settings.json.example` to `local.settings.json` and fill in your Azure credentials:

* `AZURE_ACCOUNT_NAME` / `AZURE_ACCOUNT_KEY`
* `TRANSLATOR_TEXT_SUBSCRIPTION_KEY` / `TRANSLATOR_TEXT_ENDPOINT`
* (Optional) OneDrive OAuth: `CLIENT_ID`, `SECRET_ID`, `TENANT_ID`

To run locally:

```bash
func start --python
```

Local base URL: `http://localhost:7071`

---

## 📆 Azure Deployment

```powershell
az login
./deploy.ps1 -ResourceGroupName "my-rg" -FunctionAppName "translator-func" -CreateResources
```

* `-CreateResources` creates Azure Storage, Translator, and the Function App.
* Function key-based auth is enabled by default. Use `?code=...` in URLs for manual testing.

---

## 📄 API Overview

| Endpoint                       | Method | Description                      |
| ------------------------------ | ------ | -------------------------------- |
| `/api/health`                  | GET    | Health check                     |
| `/api/start_translation`       | POST   | Start a new document translation |
| `/api/check_status/{id}`       | GET    | Check translation status         |
| `/api/get_result/{id}`         | GET    | Retrieve translated file         |
| `/api/cancel_translation/{id}` | DELETE | Cancel a translation in progress |
| `/api/languages`               | GET    | List supported languages         |
| `/api/formats`                 | GET    | List supported file formats      |

**Example:**

```bash
curl -X POST https://<your-func>.azurewebsites.net/api/start_translation \
  -H "Content-Type: application/json" \
  -d '{
        "file_content": "<BASE64_STRING>",
        "file_name": "doc.pdf",
        "target_language": "fr",
        "user_id": "user123"
      }'
```

---

## 📁 Project Structure

```
Translation__MCP_func-v1/
├── function_app.py
├── host.json
├── requirements.txt
├── local.settings.json.example
├── deploy.ps1
├── shared/
│   ├── config.py
│   ├── models/schemas.py
│   ├── services/
│   │   ├── translation_service.py
│   │   ├── blob_service.py
│   │   ├── graph_service.py
│   │   ├── translation_handler.py
│   │   ├── status_handler.py
│   │   └── state_manager.py
│   └── utils/response_helper.py
└── tests/
```

---

## 🚫 Security & Authentication

* By default, Functions require `?code=<FUNCTION_KEY>` in the URL.
* You may enable Azure AD auth or set function access level to `anonymous` for public endpoints.
* All secrets should be stored securely in Azure App Settings or Key Vault.

---

## ✅ Testing

Unit tests are located under `tests/` and use `pytest`.

```bash
pytest
```

CI/CD with GitHub Actions ensures tests are run on each commit.

---

## 👍 Contributing

Feel free to fork this repo and submit pull requests! Contributions are welcome:

* Bug fixes
* Documentation
* Feature improvements

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> Migrating to Azure Functions helps significantly reduce cloud costs while preserving full translation features. It’s ideal for production and scalable use-cases.
