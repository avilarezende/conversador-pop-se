"""Configurações compartilhadas do Conversador PoP-SE."""

from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LlmProvider = Literal["ollama", "gemini", "openai", "azure", "grok"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    engine_env: Literal["development", "staging", "production"] = "development"

    # --- Banco e RAG ---
    database_url: str = "postgresql+asyncpg://popse:altere_em_producao@postgres:5432/conversador"
    chroma_path: str = "/data/chroma"
    config_path: str = "/app/config"
    popse_context_url: str = "https://www.pop-se.rnp.br"

    # --- Segurança da API (obrigatório em produção) ---
    # Token compartilhado usado pelos módulos (WhatsApp/Telegram/Discord/coletores)
    # para autenticar contra o engine. Nunca use o valor padrão em produção.
    engine_api_token: str = "change-me-engine-token"

    # --- Provedor de IA ---
    # Valores: ollama | gemini | openai | azure | grok
    llm_provider: LlmProvider = "ollama"

    # Origens CORS permitidas (separadas por vírgula). Vazio/ausente = sem
    # CORS habilitado; defina explicitamente os domínios do portal e canais,
    # ex.: "https://painel.pop-se.rnp.br".
    cors_origins: str = ""

    # Ollama (local, gratuito)
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "llama3.2:3b"

    # Google Gemini (API key em https://aistudio.google.com/apikey)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-flash-latest"

    # OpenAI (API key em https://platform.openai.com/api-keys)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None  # opcional: proxy compatível OpenAI

    # Azure OpenAI (portal Azure → recurso OpenAI → Keys and Endpoint)
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None  # ex.: https://SEU-RECURSO.openai.azure.com
    azure_openai_deployment: str | None = None  # nome do deployment no Azure
    azure_openai_api_version: str = "2024-08-01-preview"

    # xAI Grok (API key em https://console.x.ai)
    grok_api_key: str | None = None
    grok_model: str = "grok-2-latest"
    grok_base_url: str = "https://api.x.ai/v1"

    @model_validator(mode="after")
    def validate_production(self):
        if self.engine_env in {"staging", "production"}:
            token = self.engine_api_token
            if len(token) < 32 or any(
                s in token.lower() for s in ("change-me", "test-", "example")
            ):
                raise ValueError("ENGINE_API_TOKEN forte é obrigatório fora de development")
            db = urlparse(self.database_url)
            password = unquote(db.password or "")
            if db.scheme != "postgresql+asyncpg" or len(password) < 16:
                raise ValueError("DATABASE_URL requer PostgreSQL e credencial própria forte")
            if password in {"altere_em_producao", "devpassword", "change-me"}:
                raise ValueError("DATABASE_URL não pode usar credenciais de exemplo")
            if any(
                origin and not origin.startswith("https://")
                for origin in self.cors_origins.split(",")
            ):
                raise ValueError("CORS de produção requer origens HTTPS explícitas")
        return self

    @property
    def config_dir(self) -> Path:
        return Path(self.config_path)


settings = Settings()
