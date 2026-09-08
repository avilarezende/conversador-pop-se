"""Catálogo de provedores de IA e modelos pré-configurados para a administração."""

# Cada provedor lista os campos de credencial que precisa e modelos sugeridos.
PROVIDER_CATALOG: list[dict] = [
    {
        "id": "ollama",
        "label": "Ollama (local, gratuito)",
        "credential_fields": ["ollama_host"],
        "models": ["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b", "mistral", "phi3"],
        "default_model": "llama3.2:3b",
        "needs_api_key": False,
    },
    {
        "id": "gemini",
        "label": "Google Gemini",
        "credential_fields": ["gemini_api_key"],
        "models": [
            "gemini-flash-latest",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-flash-lite-latest",
            "gemini-pro-latest",
        ],
        "default_model": "gemini-flash-latest",
        "needs_api_key": True,
    },
    {
        "id": "openai",
        "label": "OpenAI",
        "credential_fields": ["openai_api_key", "openai_base_url"],
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1", "o4-mini"],
        "default_model": "gpt-4o-mini",
        "needs_api_key": True,
    },
    {
        "id": "azure",
        "label": "Azure OpenAI",
        "credential_fields": [
            "azure_openai_api_key",
            "azure_openai_endpoint",
            "azure_openai_deployment",
        ],
        "models": ["(usar deployment)"],
        "default_model": "(usar deployment)",
        "needs_api_key": True,
    },
    {
        "id": "grok",
        "label": "xAI Grok",
        "credential_fields": ["grok_api_key", "grok_base_url"],
        "models": ["grok-2-latest", "grok-2", "grok-beta"],
        "default_model": "grok-2-latest",
        "needs_api_key": True,
    },
]

PROVIDER_IDS = {p["id"] for p in PROVIDER_CATALOG}
