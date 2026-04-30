# TranslateAPI Python SDK

[![PyPI version](https://img.shields.io/pypi/v/translate-api.svg)](https://pypi.org/project/translate-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/translate-api.svg)](https://pypi.org/project/translate-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-deeptranslate.online-blue.svg)](https://deeptranslate.online/docs)

Official Python client library for the TranslateAPI translation service. Translate text, documents, and images between 70+ languages with a simple, intuitive interface.

## Features

- **Text Translation**: Translate text between 70+ languages
- **Document Translation**: Support for PDF, DOCX, TXT files
- **Image OCR**: Extract and translate text from images
- **Language Detection**: Automatically detect language of text
- **Batch Translation**: Translate multiple texts in a single request
- **Account Management**: Check usage, credits, and account info

## Installation

### From PyPI (Recommended)

```bash
pip install translate-api
```

### From Source

```bash
git clone https://github.com/forcekeys/translate-api-python.git
cd translate-api-python
pip install -e .
```

## Quick Start

### 1. Get Your API Key

First, sign up at [deeptranslate.online](https://deeptranslate.online) to get your free API key.

### 2. Basic Usage

```python
from translate import TranslateAPI

# Initialize with your API key
api = TranslateAPI("your_api_key_here")

# Translate text
result = api.translate("Hello, world!", source="en", target="fr")
print(f"Translated: {result.translated_text}")
print(f"Characters used: {result.characters_used}")
print(f"Processing time: {result.processing_time_ms}ms")

# Auto-detect source language
result = api.translate("Bonjour le monde", target="en")
print(f"Detected language: {result.source_lang}")
print(f"Translated: {result.translated_text}")
```

## Comprehensive Examples

### Text Translation

```python
from translate import TranslateAPI

api = TranslateAPI("your_api_key_here")

# Basic translation
result = api.translate(
    text="Hello, how are you?",
    source="en",
    target="es"
)

# With formality control
result = api.translate(
    text="Hello, how are you?",
    source="en",
    target="de",
    formality="formal"  # or "informal"
)

# Translation with context
result = api.translate(
    text="The bank is closed on Sunday.",
    source="en",
    target="fr",
    context="financial"  # Helps with ambiguous words
)
```

### Document Translation

```python
# Translate a document file
result = api.translate_document(
    file_path="document.pdf",
    source="en",
    target="es"
)

# Save translated text to file
with open("translated_document.txt", "w") as f:
    f.write(result.translated_text)

print(f"Translated {result.pages} pages")
print(f"Used {result.characters_used} characters")
```

### Image OCR and Translation

```python
# Extract text from image and translate
result = api.ocr_and_translate(
    image_path="receipt.png",
    source="en",
    target="fr"
)

print(f"Extracted text: {result.extracted_text}")
print(f"Translated text: {result.translated_text}")
print(f"Confidence: {result.confidence}%")
```

### Language Detection

```python
# Detect language of text
detection = api.detect("Bonjour le monde")

print(f"Detected language: {detection.language}")
print(f"Language name: {detection.language_name}")
print(f"Confidence: {detection.confidence}%")

# Show alternative possibilities
for alt in detection.alternatives:
    print(f"  - {alt.language}: {alt.confidence}%")
```

### Batch Translation

```python
# Translate multiple texts at once
texts = [
    "Hello",
    "Goodbye",
    "Thank you",
    "Please"
]

results = api.batch_translate(
    texts=texts,
    source="en",
    target="de"
)

for item in results.translations:
    print(f"{item.original} => {item.translated}")
```

### Account Information

```python
# Get account details
account = api.account()

print(f"Email: {account.email}")
print(f"Plan: {account.plan}")
print(f"Status: {account.status}")

# Usage statistics
limits = account.plan_limits
print(f"Daily translations: {limits.today_used}/{limits.daily_translations}")
print(f"Remaining today: {limits.remaining_today}")

# Balance information
balance = account.balance
print(f"Available balance: ${balance.available:.2f}")
print(f"Total spent: ${balance.total_spent:.2f}")
```

### Supported Languages

```python
# Get all supported languages
languages = api.languages()

print(f"Total languages: {languages.count}")
for lang in languages.languages:
    print(f"{lang.flag} {lang.code}: {lang.name}")

# Filter by region
european_languages = [lang for lang in languages.languages if lang.region == "Europe"]
```

## Advanced Configuration

### Custom Base URL

```python
# For development or custom deployments
api = TranslateAPI(
    api_key="your_api_key",
     base_url="https://api.deeptranslate.online/api/v1",
    timeout=30,  # Request timeout in seconds
    retries=3    # Number of retry attempts
)
```

### Environment Variables

```python
import os
from translate import TranslateAPI

# Read API key from environment variable
api_key = os.environ.get("FORCEKEYS_API_KEY")
api = TranslateAPI(api_key)
```

### Error Handling

```python
from translate import TranslateAPI, APIError

api = TranslateAPI("your_api_key")

try:
    result = api.translate("Hello", source="en", target="fr")
except APIError as e:
    print(f"API Error: {e.code} - {e.message}")
    print(f"Status Code: {e.status_code}")
    
    if e.code == "rate_limit_exceeded":
        print(f"Retry after: {e.retry_after} seconds")
    elif e.code == "insufficient_credits":
        print("Please add credits to your account")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### TranslateAPI Class

```python
TranslateAPI(api_key, base_url="https://api.deeptranslate.online/api/v1", timeout=30, retries=3)
```

#### Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `translate(text, source=None, target, formality=None, context=None)` | Translate text | `text`: Text to translate<br>`source`: Source language code (auto-detected if None)<br>`target`: Target language code<br>`formality`: "formal" or "informal"<br>`context`: Context hint |
| `translate_document(file_path, source=None, target)` | Translate document file | `file_path`: Path to document (PDF, DOCX, TXT)<br>`source`: Source language code<br>`target`: Target language code |
| `ocr_and_translate(image_path, source=None, target, enhance=False)` | Extract text from image and translate | `image_path`: Path to image file<br>`source`: Source language code<br>`target`: Target language code<br>`enhance`: Apply image enhancement |
| `detect(text)` | Detect language of text | `text`: Text to analyze |
| `batch_translate(texts, source=None, target)` | Translate multiple texts | `texts`: List of texts to translate<br>`source`: Source language code<br>`target`: Target language code |
| `languages()` | Get supported languages | |
| `account()` | Get account information | |

### Response Objects

All methods return typed response objects with the following common attributes:

- `status`: "success" or "error"
- `processing_time_ms`: Processing time in milliseconds
- `characters_used`: Number of characters used

#### Translation Response
- `translated_text`: Translated text
- `source_lang`: Source language code
- `target_lang`: Target language code

#### Document Translation Response
- `translated_text`: Translated text
- `pages`: Number of pages processed
- `characters_used`: Characters used

#### OCR Response
- `extracted_text`: Text extracted from image
- `translated_text`: Translated text (if translation requested)
- `confidence`: OCR confidence percentage
- `language_detected`: Detected language in image

#### Detection Response
- `language`: Detected language code
- `language_name`: Full language name
- `confidence`: Detection confidence percentage
- `alternatives`: List of alternative possibilities

#### Account Response
- `email`: User email
- `plan`: Subscription plan
- `status`: Account status
- `plan_limits`: Dictionary with usage limits
- `balance`: Dictionary with balance information
- `statistics`: Usage statistics

## Error Codes

The SDK raises `APIError` exceptions for API errors:

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `invalid_request` | Missing or malformed parameters | 400 |
| `unauthorized` | Invalid or missing API key | 401 |
| `forbidden` | Feature not available on your plan | 403 |
| `payload_too_large` | File or text exceeds size limit | 413 |
| `unsupported_language` | Language code not supported | 422 |
| `rate_limit_exceeded` | Too many requests | 429 |
| `insufficient_credits` | Not enough credits | 402 |
| `internal_error` | Server error | 500 |

## Rate Limits

Rate limits vary by plan:

| Plan | Requests/Minute | Monthly Requests | Max Characters/Request |
|------|----------------|------------------|------------------------|
| Free | 10 | 500/day | 2,000 |
| Starter | 60 | 50,000 | 5,000 |
| Professional | 300 | 1,000,000 | 10,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Documentation**: [deeptranslate.online/docs](https://deeptranslate.online/docs)
- **Issues**: [GitHub Issues](https://github.com/forcekeys/translate-api-python/issues)
- **Email**: support@deeptranslate.online
- **Discord**: [Join our Discord](https://discord.gg/forcekeys)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [TranslateAPI JavaScript SDK](https://github.com/forcekeys/translate-api-js)
- [TranslateAPI PHP SDK](https://github.com/forcekeys/translate-api-php)
- [TranslateAPI Java SDK](https://github.com/forcekeys/translate-api-java)
- [TranslateAPI .NET SDK](https://github.com/forcekeys/translate-api-dotnet)
- [TranslateAPI Shell](https://github.com/forcekeys/translate-api-shell)
