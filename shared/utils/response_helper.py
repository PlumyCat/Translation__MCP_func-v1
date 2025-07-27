"""
Helpers pour les réponses HTTP Azure Functions
"""

import json
import logging
from typing import Dict, Any, Optional
import azure.functions as func
from datetime import datetime

logger = logging.getLogger(__name__)


def create_response(data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> func.HttpResponse:
    """
    Crée une réponse HTTP standardisée pour Azure Functions
    """
    try:
        # Headers par défaut
        default_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Timestamp': datetime.utcnow().isoformat() + 'Z',
            'X-Service': 'Azure-Functions-Translation'
        }
        
        if headers:
            default_headers.update(headers)
        
        # Ajout des headers CORS si nécessaire
        if 'Access-Control-Allow-Origin' not in default_headers:
            default_headers['Access-Control-Allow-Origin'] = '*'
            default_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            default_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        
        # Sérialisation des données
        if isinstance(data, dict):
            # Ajout des métadonnées de réponse
            response_data = {
                'success': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'data': data
            }
        else:
            response_data = {
                'success': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'result': data
            }
        
        json_data = json.dumps(response_data, ensure_ascii=False, indent=2)
        
        return func.HttpResponse(
            body=json_data,
            status_code=status_code,
            headers=default_headers,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur création réponse: {str(e)}")
        return create_error_response("Erreur de sérialisation", 500)


def create_error_response(message: str, status_code: int = 400, 
                         error_code: Optional[str] = None,
                         details: Optional[Dict[str, Any]] = None) -> func.HttpResponse:
    """
    Crée une réponse d'erreur standardisée
    """
    try:
        error_data = {
            'success': False,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': {
                'message': message,
                'status_code': status_code
            }
        }
        
        if error_code:
            error_data['error']['code'] = error_code
            
        if details:
            error_data['error']['details'] = details
        
        # Headers avec CORS
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Timestamp': datetime.utcnow().isoformat() + 'Z',
            'X-Service': 'Azure-Functions-Translation',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        }
        
        json_data = json.dumps(error_data, ensure_ascii=False, indent=2)
        
        return func.HttpResponse(
            body=json_data,
            status_code=status_code,
            headers=headers,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur création réponse d'erreur: {str(e)}")
        # Réponse d'erreur minimale en cas de problème de sérialisation
        return func.HttpResponse(
            body='{"success": false, "error": {"message": "Erreur interne du serveur"}}',
            status_code=500,
            headers={'Content-Type': 'application/json'},
            mimetype='application/json'
        )


def create_health_response(service_status: Dict[str, Any]) -> func.HttpResponse:
    """
    Crée une réponse spécifique pour le health check
    """
    try:
        # Détermination du statut global
        all_services_ok = all(
            status in ['available', 'healthy', 'ok'] 
            for status in service_status.get('services', {}).values()
        )
        
        overall_status = 'healthy' if all_services_ok else 'degraded'
        status_code = 200 if all_services_ok else 503
        
        health_data = {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'environment': 'azure-functions',
            **service_status
        }
        
        return create_response(health_data, status_code)
        
    except Exception as e:
        logger.error(f"❌ Erreur health check: {str(e)}")
        return create_error_response("Health check failed", 503)


def create_cors_preflight_response() -> func.HttpResponse:
    """
    Crée une réponse pour les requêtes OPTIONS (CORS preflight)
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Max-Age': '86400',  # 24 heures
        'Content-Length': '0'
    }
    
    return func.HttpResponse(
        body='',
        status_code=204,
        headers=headers
    )


def validate_json_request(req: func.HttpRequest, required_fields: list = None) -> tuple:
    """
    Valide une requête JSON et retourne les données ou une erreur
    
    Returns:
        tuple: (success: bool, data_or_error_response: dict|HttpResponse)
    """
    try:
        # Vérification du corps de la requête
        if not req.get_body():
            return False, create_error_response("Corps de requête manquant", 400)
        
        # Parse du JSON
        try:
            request_data = req.get_json()
        except ValueError as e:
            return False, create_error_response(f"JSON invalide: {str(e)}", 400)
        
        if not isinstance(request_data, dict):
            return False, create_error_response("Le corps doit être un objet JSON", 400)
        
        # Validation des champs requis
        if required_fields:
            missing_fields = [field for field in required_fields if field not in request_data]
            if missing_fields:
                return False, create_error_response(
                    f"Champs manquants: {', '.join(missing_fields)}", 
                    400,
                    error_code="MISSING_FIELDS",
                    details={"missing_fields": missing_fields}
                )
        
        return True, request_data
        
    except Exception as e:
        logger.error(f"❌ Erreur validation requête: {str(e)}")
        return False, create_error_response("Erreur de validation", 500)


def extract_user_id(req: func.HttpRequest) -> Optional[str]:
    """
    Extrait l'ID utilisateur depuis les headers ou les paramètres
    """
    try:
        # Essayer depuis les headers
        user_id = req.headers.get('X-User-ID') or req.headers.get('User-ID')
        
        if not user_id:
            # Essayer depuis les paramètres de requête
            user_id = req.params.get('user_id')
        
        if not user_id:
            # Essayer depuis le corps JSON
            try:
                json_data = req.get_json()
                if json_data and isinstance(json_data, dict):
                    user_id = json_data.get('user_id')
            except:
                pass
        
        return user_id.strip() if user_id else None
        
    except Exception as e:
        logger.error(f"❌ Erreur extraction user_id: {str(e)}")
        return None


def log_request(req: func.HttpRequest, user_id: Optional[str] = None) -> None:
    """
    Log les détails d'une requête pour le débogage
    """
    try:
        logger.info(f"📝 Requête: {req.method} {req.url}")
        logger.info(f"👤 User ID: {user_id or 'Non spécifié'}")
        logger.info(f"🌐 IP: {req.headers.get('X-Forwarded-For', 'Unknown')}")
        logger.info(f"🔧 User-Agent: {req.headers.get('User-Agent', 'Unknown')[:100]}")
        
        # Log des paramètres (sans les données sensibles)
        if req.params:
            safe_params = {k: v for k, v in req.params.items() 
                          if k.lower() not in ['password', 'secret', 'key', 'token']}
            if safe_params:
                logger.info(f"📋 Paramètres: {safe_params}")
        
    except Exception as e:
        logger.error(f"❌ Erreur log requête: {str(e)}")


def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille de fichier en unités lisibles
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    Formate une durée en format lisible
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"