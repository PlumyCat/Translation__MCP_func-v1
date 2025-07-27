# 🧪 Guide de Test - Workflow Complet

Ce guide explique comment tester le workflow complet de traduction avec vos fonctions Azure.

## 🔄 Workflow de Test Complet

### 1. Démarrer une Traduction
```http
POST http://localhost:7071/api/start_translation
Content-Type: application/json

{
  "blob_name": "document-test.pdf",
  "user_id": "test-user-12345", 
  "target_language": "fr"
}
```

**Réponse attendue:**
```json
{
  "success": false,
  "error": {
    "message": "Fichier 'document-test.pdf' non trouvé",
    "status_code": 404
  }
}
```
> ✅ **Normal** - Le fichier n'existe pas dans le blob storage

### 2. Vérifier le Statut d'une Traduction

#### Test avec un ID réel (de votre test précédent):
```http
GET http://localhost:7071/api/check_status/e72ea58f-ee5c-4bc1-adba-085479a09395
```

**Réponse attendue:**
```json
{
  "success": true,
  "data": {
    "translation_id": "e72ea58f-ee5c-4bc1-adba-085479a09395",
    "status": "Succeeded",
    "progress": "Progression: 1/1 (100.0%)",
    "created_at": "2025-07-27T02:40:45.7762658Z",
    "last_updated": "2025-07-27T02:40:48.5988028Z",
    "summary": {
      "total": 1,
      "failed": 0,
      "success": 1,
      "in_progress": 0
    }
  }
}
```
> ✅ **Parfait** - La traduction est terminée avec succès

#### Test avec un ID inexistant:
```http
GET http://localhost:7071/api/check_status/test-invalid-id
```

**Réponse attendue:**
```json
{
  "success": true,
  "data": {
    "translation_id": "test-invalid-id",
    "status": "Failed",
    "error": "Erreur HTTP 404: "
  }
}
```
> ✅ **Normal** - L'ID n'existe pas dans Azure Translator

## 🎯 Tests des Autres Endpoints

### Health Check
```bash
curl http://localhost:7071/api/health
```

### Langues Supportées
```bash
curl http://localhost:7071/api/languages
```

### Formats Supportés  
```bash
curl http://localhost:7071/api/formats
```

## 🔧 Problème Résolu

### ❌ Avant (Problème)
```
GET /api/check_status/{translation_id}
```
- La route paramétrisée ne fonctionnait pas
- `function.json` n'avait pas de configuration de route
- Le code utilisait encore Azure Functions v2

### ✅ Après (Résolu)
```json
// function.json
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger", 
      "direction": "in",
      "name": "req",
      "methods": ["get"],
      "route": "check_status/{translation_id}"  // ← Route paramétrisée ajoutée
    }
  ]
}
```

```python
# __init__.py 
def main(req: func.HttpRequest) -> func.HttpResponse:
    translation_id = req.route_params.get('translation_id')  # ← Récupération du paramètre
```

## 🚀 Workflow de Production

### Étape 1: Upload d'un fichier dans Azure Storage
```bash
# Avec Azure CLI
az storage blob upload \
  --account-name YOUR_STORAGE \
  --container-name doc-to-trad \
  --name "document.pdf" \
  --file "./local-document.pdf"
```

### Étape 2: Démarrer la traduction
```http
POST /api/start_translation
{
  "blob_name": "document.pdf",
  "user_id": "user123",
  "target_language": "fr"
}
```

### Étape 3: Suivre le statut
```http
GET /api/check_status/{returned_translation_id}
```

### Étape 4: Récupérer le résultat
```http
POST /api/get_result
{
  "blob_name": "document.pdf",
  "user_id": "user123", 
  "target_language": "fr"
}
```

## 🎉 Statuts de Traduction

| Statut | Description | Action |
|--------|-------------|--------|
| `Pending` | En attente de traitement | Attendre |
| `InProgress` | Traduction en cours | Vérifier régulièrement |
| `Succeeded` | ✅ Traduction terminée | Récupérer le résultat |
| `Failed` | ❌ Traduction échouée | Vérifier l'erreur |

## 💡 Conseils de Test

1. **Utilisez le fichier `test.http`** avec VS Code + extension REST Client
2. **Remplacez `@translationId`** avec un vrai ID de traduction
3. **Testez d'abord localement** avec `func start --python`
4. **Vérifiez les logs** dans la console Azure Functions
5. **Pour tester avec de vrais fichiers**, uploadez d'abord dans le blob storage

L'endpoint `check_status` fonctionne maintenant parfaitement ! 🎉