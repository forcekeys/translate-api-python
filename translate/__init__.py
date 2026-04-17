"""
TranslateAPI Python SDK
Official Python client for the TranslateAPI translation service.
https://github.com/forcekeys/translate-api-python
"""

import os
import json
import time
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

BASE_URL = "https://api.translate.forcekeys.com/api/v1"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3


class Formality(str, Enum):
    """Translation formality levels"""
    FORMAL = "formal"
    INFORMAL = "informal"


class APIError(Exception):
    """API error exception"""
    
    def __init__(self, message: str, code: str = None, status_code: int = None, 
                 retry_after: int = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(self.message)


@dataclass
class Language:
    """Language information"""
    code: str
    name: str
    native_name: str
    flag: str = ""
    supports_formality: bool = False


@dataclass
class TranslationOptions:
    """Translation options"""
    formality: Optional[Formality] = None
    context: Optional[str] = None
    preserve_formatting: bool = False
    split_sentences: bool = True


@dataclass
class TranslationResult:
    """Translation result"""
    translated_text: str
    source_lang: str
    target_lang: str
    detected_lang: Optional[str] = None
    characters_used: int = 0
    processing_time_ms: int = 0
    formality: Optional[str] = None


@dataclass
class DocumentTranslationResult:
    """Document translation result"""
    translated_text: str
    source_lang: str
    target_lang: str
    pages: int = 0
    characters_used: int = 0
    processing_time_ms: int = 0
    file_format: str = ""


@dataclass
class OCRResult:
    """OCR and translation result"""
    extracted_text: str
    translated_text: str
    confidence: float = 0.0
    language_detected: str = ""
    processing_time_ms: int = 0
    characters_used: int = 0


@dataclass
class LanguageAlternative:
    """Language detection alternative"""
    language: str
    confidence: float
    language_name: str = ""


@dataclass
class LanguageDetectionResult:
    """Language detection result"""
    language: str
    language_name: str
    confidence: float
    alternatives: List[LanguageAlternative] = field(default_factory=list)
    processing_time_ms: int = 0


@dataclass
class BatchTranslationItem:
    """Batch translation item"""
    original: str
    translated: str
    source_lang: str = ""
    target_lang: str = ""


@dataclass
class BatchTranslationResult:
    """Batch translation result"""
    translations: List[BatchTranslationItem]
    characters_used: int = 0
    processing_time_ms: int = 0


@dataclass
class PlanLimits:
    """Plan limits"""
    daily_translations: int = 0
    today_used: int = 0
    remaining_today: int = 0
    percentage_used: float = 0.0


@dataclass
class BalanceInfo:
    """Balance information"""
    available: float = 0.0
    total_spent: float = 0.0
    currency: str = "USD"


@dataclass
class Statistics:
    """Usage statistics"""
    total_translations: int = 0
    total_characters: int = 0
    total_documents: int = 0
    total_images: int = 0


@dataclass
class AccountInfo:
    """Account information"""
    email: str
    name: str = ""
    plan: str = "free"
    status: str = "active"
    plan_limits: PlanLimits = field(default_factory=PlanLimits)
    balance: BalanceInfo = field(default_factory=BalanceInfo)
    statistics: Statistics = field(default_factory=Statistics)
    api_key_name: str = ""
    api_key_status: str = "active"
    created_at: str = ""
    last_used: str = ""


@dataclass
class LanguageList:
    """Language list"""
    count: int = 0
    languages: List[Language] = field(default_factory=list)


class TranslateAPI:
    """
    TranslateAPI Python client
    
    Example:
        >>> from translate import TranslateAPI
        >>> api = TranslateAPI("your_api_key")
        >>> result = api.translate("Hello, world!", "en", "fr")
        >>> print(result.translated_text)
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL, 
                 timeout: int = DEFAULT_TIMEOUT, retries: int = DEFAULT_RETRIES,
                 session: Optional[requests.Session] = None):
        """
        Initialize TranslateAPI client
        
        Args:
            api_key: Your API key (or set TRANSLATE_API_KEY environment variable)
            base_url: API base URL
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            session: Custom requests session
        """
        self.api_key = api_key or os.environ.get("TRANSLATE_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as argument or set "
                "TRANSLATE_API_KEY environment variable."
            )
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, files: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            files: Files to upload
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            APIError: If API returns an error
            RequestException: If network error occurs
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"TranslateAPI-Python/1.0.0"
        }
        
        if files:
            headers.pop("Content-Type", None)
        elif method != "GET":
            headers["Content-Type"] = "application/json"
        
        last_exception = None
        
        for attempt in range(self.retries):
            try:
                if method == "GET":
                    response = self.session.get(
                        url, headers=headers, params=params, timeout=self.timeout
                    )
                elif method == "POST":
                    if files:
                        response = self.session.post(
                            url, headers=headers, data=data, files=files, 
                            timeout=self.timeout
                        )
                    else:
                        response = self.session.post(
                            url, headers=headers, json=data, timeout=self.timeout
                        )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "error":
                    error_code = result.get("code", "unknown_error")
                    error_msg = result.get("message", "Unknown error")
                    retry_after = result.get("retry_after")
                    
                    raise APIError(
                        message=error_msg,
                        code=error_code,
                        status_code=response.status_code,
                        retry_after=retry_after
                    )
                
                return result
                
            except (RequestException, Timeout) as e:
                last_exception = e
                if attempt < self.retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                continue
            except HTTPError as e:
                if e.response.status_code >= 500:
                    # Retry on server errors
                    last_exception = e
                    if attempt < self.retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                    continue
                else:
                    # Don't retry on client errors
                    try:
                        error_data = e.response.json()
                        error_code = error_data.get("code", "http_error")
                        error_msg = error_data.get("message", str(e))
                    except:
                        error_code = "http_error"
                        error_msg = str(e)
                    
                    raise APIError(
                        message=error_msg,
                        code=error_code,
                        status_code=e.response.status_code
                    )
        
        # If we get here, all retries failed
        raise APIError(
            message=f"Request failed after {self.retries} attempts: {last_exception}",
            code="request_failed"
        )
    
    def translate(self, text: str, source: Optional[str] = None, 
                  target: str = "en", options: Optional[TranslationOptions] = None) -> TranslationResult:
        """
        Translate text
        
        Args:
            text: Text to translate
            source: Source language code (None for auto-detection)
            target: Target language code
            options: Translation options
            
        Returns:
            Translation result
        """
        data = {
            "text": text,
            "target_lang": target
        }
        
        if source:
            data["source_lang"] = source
        
        if options:
            if options.formality:
                data["formality"] = options.formality.value
            if options.context:
                data["context"] = options.context
            if options.preserve_formatting is not None:
                data["preserve_formatting"] = options.preserve_formatting
            if options.split_sentences is not None:
                data["split_sentences"] = options.split_sentences
        
        result = self._make_request("translate", method="POST", data=data)
        
        return TranslationResult(
            translated_text=result["translated_text"],
            source_lang=result.get("source_lang", source or "auto"),
            target_lang=result["target_lang"],
            detected_lang=result.get("detected_language"),
            characters_used=result.get("characters_used", 0),
            processing_time_ms=result.get("processing_time_ms", 0),
            formality=result.get("formality")
        )
    
    def translate_document(self, file_path: str, source: Optional[str] = None, 
                          target: str = "en") -> DocumentTranslationResult:
        """
        Translate document file
        
        Args:
            file_path: Path to document file (PDF, DOCX, TXT)
            source: Source language code (None for auto-detection)
            target: Target language code
            
        Returns:
            Document translation result
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"target_lang": target}
            
            if source:
                data["source_lang"] = source
            
            result = self._make_request(
                "translate/document", method="POST", data=data, files=files
            )
        
        return DocumentTranslationResult(
            translated_text=result["translated_text"],
            source_lang=result.get("source_lang", source or "auto"),
            target_lang=result["target_lang"],
            pages=result.get("pages", 0),
            characters_used=result.get("characters_used", 0),
            processing_time_ms=result.get("processing_time_ms", 0),
            file_format=result.get("file_format", "")
        )
    
    def ocr_and_translate(self, image_path: str, source: Optional[str] = None,
                         target: str = "en", enhance: bool = False) -> OCRResult:
        """
        Extract text from image and translate
        
        Args:
            image_path: Path to image file
            source: Source language code (None for auto-detection)
            target: Target language code
            enhance: Apply image enhancement
            
        Returns:
            OCR and translation result
        """
        with open(image_path, "rb") as f:
            files = {"image": (os.path.basename(image_path), f)}
            data = {"target_lang": target, "enhance": enhance}
            
            if source:
                data["source_lang"] = source
            
            result = self._make_request(
                "ocr", method="POST", data=data, files=files
            )
        
        return OCRResult(
            extracted_text=result["text"],
            translated_text=result.get("translated_text", ""),
            confidence=result.get("confidence", 0.0),
            language_detected=result.get("language_detected", ""),
            processing_time_ms=result.get("processing_time_ms", 0),
            characters_used=result.get("characters_used", 0)
        )
    
    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language detection result
        """
        data = {"text": text}
        result = self._make_request("detect", method="POST", data=data)
        
        alternatives = []
        for alt in result.get("alternatives", []):
            alternatives.append(LanguageAlternative(
                language=alt["language"],
                confidence=alt["confidence"],
                language_name=alt.get("language_name", "")
            ))
        
        return LanguageDetectionResult(
            language=result["language"],
            language_name=result.get("language_name", ""),
            confidence=result.get("confidence", 0.0),
            alternatives=alternatives,
            processing_time_ms=result.get("processing_time_ms", 0)
        )
    
    def batch_translate(self, texts: List[str], source: Optional[str] = None,
                       target: str = "en") -> BatchTranslationResult:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source: Source language code (None for auto-detection)
            target: Target language code
            
        Returns:
            Batch translation result
        """
        data = {
            "texts": texts,
            "target_lang": target
        }
        
        if source:
            data["source_lang"] = source
        
        result = self._make_request("translate/batch", method="POST", data=data)
        
        translations = []
        for item in result.get("translations", []):
            translations.append(BatchTranslationItem(
                original=item["original"],
                translated=item["translated"],
                source_lang=source or "auto",
                target_lang=target
            ))
        
        return BatchTranslationResult(
            translations=translations,
            characters_used=result.get("characters_used", 0),
            processing_time_ms=result.get("processing_time_ms", 0)
        )
    
    def get_languages(self) -> LanguageList:
        """
        Get supported languages
        
        Returns:
            Language list
        """
        result = self._make_request("languages", method="GET")
        
        languages = []
        for lang in result.get("languages", []):
            languages.append(Language(
                code=lang["code"],
                name=lang["name"],
                native_name=lang.get("native_name", lang["name"]),
                flag=lang.get("flag", ""),
                supports_formality=lang.get("supports_formality", False)
            ))
        
        return LanguageList(
            count=result.get("count", len(languages)),
            languages=languages
        )
    
    def get_account(self) -> AccountInfo:
        """
        Get account information
        
        Returns:
            Account information
        """
        result = self._make_request("account", method="GET")
        account_data = result.get("account", {})
        
        plan_limits_data = account_data.get("plan_limits", {})
        plan_limits = PlanLimits(
            daily_translations=plan_limits_data.get("daily_translations", 0),
            today_used=plan_limits_data.get("today_used", 0),
            remaining_today=plan_limits_data.get("remaining_today", 0),
            percentage_used=plan_limits_data.get("percentage_used", 0.0)
        )
        
        balance_data = account_data.get("balance", {})
        balance = BalanceInfo(
            available=balance_data.get("available", 0.0),
            total_spent=balance_data.get("total_spent", 0.0),
            currency=balance_data.get("currency", "USD")
        )
        
        stats_data = account_data.get("statistics", {})
        statistics = Statistics(
            total_translations=stats_data.get("total_translations", 0),
            total_characters=stats_data.get("total_characters", 0),
            total_documents=stats_data.get("total_documents", 0),
            total_images=stats_data.get("total_images", 0)
        )
        
        api_key_data = account_data.get("api_key", {})
        
        return AccountInfo(
            email=account_data.get("email", ""),
            name=account_data.get("name", ""),
            plan=account_data.get("plan", "free"),
            status=account_data.get("status", "active"),
            plan_limits=plan_limits,
            balance=balance,
            statistics=statistics,
            api_key_name=api_key_data.get("name", ""),
            api_key_status=api_key_data.get("status", "active"),
            created_at=api_key_data.get("created_at", ""),
            last_used=api_key_data.get("last_used", "")
        )
    
    def get_usage(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Usage statistics
        """
        result = self._make_request("usage", method="GET")
        return result
    
    def get_balance(self) -> BalanceInfo:
        """
        Get balance information
        
        Returns:
            Balance information
        """
        account = self.get_account()
        return account.balance
    
    def get_plan_limits(self) -> PlanLimits:
        """
        Get plan limits
        
        Returns:
            Plan limits
        """
        account = self.get_account()
        return account.plan_limits
    
    def get_statistics(self) -> Statistics:
        """
        Get usage statistics
        
        Returns:
            Usage statistics
        """
        account = self.get_account()
        return account.statistics
    
    def test_connection(self) -> bool:
        """
        Test API connection
        
        Returns:
            True if connection successful
        """
        try:
            self._make_request("languages", method="GET")
            return True
        except APIError:
            return False
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set request timeout
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
    
    def set_retries(self, retries: int) -> None:
        """
        Set number of retry attempts
        
        Args:
            retries: Number of retries
        """
        self.retries = retries
    
    def close(self) -> None:
        """
        Close the session
        """
        self.session.close()


# Convenience functions
def translate(text: str, api_key: str, source: Optional[str] = None, 
              target: str = "en", **kwargs) -> str:
    """
    Convenience function for quick translation
    
    Args:
        text: Text to translate
        api_key: API key
        source: Source language code
        target: Target language code
        **kwargs: Additional options
        
    Returns:
        Translated text
    """
    api = TranslateAPI(api_key)
    options = None
    
    if kwargs:
        options = TranslationOptions(**kwargs)
    
    result = api.translate(text, source, target, options)
    return result.translated_text


def detect_language(text: str, api_key: str) -> str:
    """
    Convenience function for language detection
    
    Args:
        text: Text to analyze
        api_key: API key
        
    Returns:
        Detected language code
    """
    api = TranslateAPI(api_key)
    result = api.detect(text)
    return result.language


def get_supported_languages(api_key: str) -> List[Language]:
    """
    Convenience function to get supported languages
    
    Args:
        api_key: API key
        
    Returns:
        List of supported languages
    """
    api = TranslateAPI(api_key)
    result = api.get_languages()
    return result.languages


__version__ = "1.0.0"
__all__ = [
    "TranslateAPI",
    "APIError",
    "Formality",
    "Language",
    "TranslationOptions",
    "TranslationResult",
    "DocumentTranslationResult",
    "OCRResult",
    "LanguageDetectionResult",
    "BatchTranslationResult",
    "AccountInfo",
    "PlanLimits",
    "BalanceInfo",
    "Statistics",
    "translate",
    "detect_language",
    "get_supported_languages"
]
