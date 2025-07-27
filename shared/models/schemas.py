"""
Schémas de données pour Azure Functions
Copiés et adaptés du code conteneur existant
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class TranslationStatus(str, Enum):
    """États possibles d'une traduction"""
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"


class TranslationRequest(BaseModel):
    """Requête de traduction de document"""
    file_content: str = Field(..., description="Contenu du fichier en base64")
    file_name: str = Field(..., description="Nom du fichier avec extension")
    target_language: str = Field(..., description="Code langue cible (ex: 'fr', 'en', 'es')")
    user_id: str = Field(..., description="Identifiant unique de l'utilisateur")


class BlobUrls(BaseModel):
    """URLs des blobs source et cible"""
    source_url: str = Field(..., description="URL SAS du blob source")
    target_url: str = Field(..., description="URL SAS du blob cible")
    input_blob_name: str = Field(..., description="Nom du blob source")
    output_blob_name: str = Field(..., description="Nom du blob cible")


class TranslationStatusResponse(BaseModel):
    """Réponse de statut de traduction"""
    status: TranslationStatus = Field(..., description="Statut de la traduction")
    original_status: Optional[str] = Field(None, description="Statut original de l'API Azure")
    progress: Optional[str] = Field(None, description="Information de progression")
    created_at: Optional[str] = Field(None, description="Date de création")
    last_updated: Optional[str] = Field(None, description="Dernière mise à jour")
    error: Optional[str] = Field(None, description="Message d'erreur si échec")
    summary: Optional[Dict[str, int]] = Field(None, description="Résumé des statistiques")


class TranslationInfo(BaseModel):
    """Informations d'une traduction active"""
    file_name: str = Field(..., description="Nom du fichier original")
    target_language: str = Field(..., description="Langue cible")
    user_id: str = Field(..., description="ID utilisateur")
    blob_urls: BlobUrls = Field(..., description="URLs des blobs")
    status: str = Field(..., description="Statut actuel")
    started_at: float = Field(..., description="Timestamp de démarrage")
    translation_id: str = Field(..., description="ID de traduction Azure")


class TranslationResult(BaseModel):
    """Résultat final d'une traduction"""
    translation_id: str = Field(..., description="ID de la traduction")
    status: TranslationStatus = Field(..., description="Statut final")
    file_name: str = Field(..., description="Nom du fichier original")
    target_language: str = Field(..., description="Langue cible")
    download_url: Optional[str] = Field(None, description="URL de téléchargement du fichier traduit")
    onedrive_url: Optional[str] = Field(None, description="URL OneDrive si upload réussi")
    created_at: str = Field(..., description="Date de création")
    completed_at: Optional[str] = Field(None, description="Date de completion")
    error: Optional[str] = Field(None, description="Message d'erreur")


class OneDriveUploadResult(BaseModel):
    """Résultat d'upload sur OneDrive"""
    success: bool = Field(..., description="Succès de l'upload")
    onedrive_url: Optional[str] = Field(None, description="URL OneDrive du fichier")
    error: Optional[str] = Field(None, description="Message d'erreur")


class FunctionResponse(BaseModel):
    """Réponse standard d'une Azure Function"""
    success: bool = Field(..., description="Succès de l'opération")
    message: str = Field(..., description="Message descriptif")
    data: Optional[Dict[str, Any]] = Field(None, description="Données additionnelles")


class SupportedLanguages:
    """Langues supportées by Azure Translator"""

    LANGUAGES = {
        "af": "Afrikaans",
        "ar": "Arabic",
        "bg": "Bulgarian",
        "bn": "Bengali",
        "bs": "Bosnian",
        "ca": "Catalan",
        "cs": "Czech",
        "cy": "Welsh",
        "da": "Danish",
        "de": "German",
        "el": "Greek",
        "en": "English",
        "es": "Spanish",
        "et": "Estonian",
        "fa": "Persian",
        "fi": "Finnish",
        "fr": "French",
        "ga": "Irish",
        "gu": "Gujarati",
        "he": "Hebrew",
        "hi": "Hindi",
        "hr": "Croatian",
        "hu": "Hungarian",
        "id": "Indonesian",
        "is": "Icelandic",
        "it": "Italian",
        "ja": "Japanese",
        "kn": "Kannada",
        "ko": "Korean",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "ml": "Malayalam",
        "mr": "Marathi",
        "ms": "Malay",
        "mt": "Maltese",
        "nb": "Norwegian",
        "nl": "Dutch",
        "pa": "Punjabi",
        "pl": "Polish",
        "pt-pt": "Portuguese",
        "ro": "Romanian",
        "ru": "Russian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "sv": "Swedish",
        "ta": "Tamil",
        "te": "Telugu",
        "th": "Thai",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "ur": "Urdu",
        "vi": "Vietnamese",
        "zh": "Chinese (Simplified)",
        "zh-Hant": "Chinese (Traditional)",
        "tlh-Latn": "Klingon (Latin)",
    }

    @classmethod
    def is_supported(cls, language_code: str) -> bool:
        """Vérifie si une langue est supportée"""
        return language_code.lower() in cls.LANGUAGES

    @classmethod
    def get_language_name(cls, language_code: str) -> Optional[str]:
        """Obtient le nom complet d'une langue"""
        return cls.LANGUAGES.get(language_code.lower())

    @classmethod
    def get_all_languages(cls) -> Dict[str, str]:
        """Retourne toutes les langues supportées"""
        return cls.LANGUAGES.copy()


class FileFormats:
    """Formats de fichiers supportés"""

    SUPPORTED_FORMATS = {
        ".pdf": "Portable Document Format",
        ".docx": "Microsoft Word Document",
        ".doc": "Microsoft Word Document (Legacy)",
        ".pptx": "Microsoft PowerPoint Presentation",
        ".ppt": "Microsoft PowerPoint Presentation (Legacy)",
        ".xlsx": "Microsoft Excel Spreadsheet",
        ".xls": "Microsoft Excel Spreadsheet (Legacy)",
        ".txt": "Plain Text File",
        ".rtf": "Rich Text Format",
        ".html": "HyperText Markup Language",
        ".htm": "HyperText Markup Language",
        ".xml": "eXtensible Markup Language",
        ".odt": "OpenDocument Text",
        ".ods": "OpenDocument Spreadsheet",
        ".odp": "OpenDocument Presentation"
    }

    @classmethod
    def is_supported(cls, file_name: str) -> bool:
        """Vérifie si le format de fichier est supporté"""
        extension = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
        return extension in cls.SUPPORTED_FORMATS

    @classmethod
    def get_format_description(cls, file_name: str) -> Optional[str]:
        """Obtient la description du format"""
        extension = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
        return cls.SUPPORTED_FORMATS.get(extension)

    @classmethod
    def get_all_formats(cls) -> Dict[str, str]:
        """Retourne tous les formats supportés"""
        return cls.SUPPORTED_FORMATS.copy()


# Fonctions utilitaires de validation
def validate_file_format(file_name: str) -> bool:
    """Valide le format d'un fichier"""
    return FileFormats.is_supported(file_name)


def validate_language_code(language_code: str) -> bool:
    """Valide un code de langue"""
    return SupportedLanguages.is_supported(language_code)


def get_file_extension(file_name: str) -> str:
    """Extrait l'extension d'un fichier"""
    return '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''