# Migrate from Container to Azure Functions

This project shows how to move your document translation service from an **Azure Container Instance** to **Azure Functions**. The goal is to lower costs while keeping the same features.

## Benefits
- **Lower cost**: pay only when the function runs.
- **Same features**: document translation via Azure Translator, optional OneDrive integration and identical APIs.
- **Improved monitoring and security** with Application Insights and automatic scaling.

## Project structure
```text
azure-functions-translation/
├── host.json                 # Azure Functions configuration
├── requirements.txt          # Python dependencies
├── local.settings.json       # Local configuration sample
├── shared/                   # Shared modules
│   ├── config.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── blob_service.py
│   │   ├── translation_service.py
│   │   ├── graph_service.py
│   │   ├── translation_handler.py
│   │   ├── status_handler.py
│   │   └── state_manager.py
│   └── utils/
│       └── response_helper.py
```

## Quick deployment
1. Install Azure CLI and Azure Functions Core Tools.
2. Copy `local.settings.json.example` to `local.settings.json` and fill in your keys.
3. Run the provided PowerShell scripts to deploy the service.

## Available endpoints
- `/api/health` – health check
- `/api/start_translation` – start a translation
- `/api/check_status/{id}` – check translation status
- `/api/get_result/{id}` – retrieve the translated file
- `/api/languages` – supported languages
- `/api/formats` – supported file formats

For full details see the deployment guide and other documentation files.
