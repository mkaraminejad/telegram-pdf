"""Configuration settings for Persian PDF to DOCX Telegram Bot.

Uses Pydantic Settings for environment variable parsing, validation, and safe defaults.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram Bot Token (Mandatory)
    TELEGRAM_BOT_TOKEN: str = Field(
        default="PLACEHOLDER_TOKEN",
        description="Telegram bot token obtained from @BotFather"
    )

    # Redis Queue & Caching
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL for Celery broker & rate limiting"
    )

    # Processing limits
    MAX_FILE_SIZE_MB: int = Field(
        default=20,
        description="Maximum allowed PDF file size in Megabytes"
    )
    MAX_PAGE_COUNT: int = Field(
        default=30,
        description="Maximum allowed pages in a single PDF document"
    )
    TEMP_FILE_TTL_HOURS: int = Field(
        default=24,
        description="Maximum retention hours for temporary files before automatic purging"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=5,
        description="Maximum number of PDF conversion requests per user per minute"
    )

    # Storage
    STORAGE_DIR: str = Field(
        default="/app/data/temp",
        description="Root temporary storage path for isolated task files"
    )

    # AI Engine (Groq / Google Gemini Multimodal & Vision Extraction)
    AI_PROVIDER: str = Field(
        default="gemini",
        description="Active AI Provider: 'groq' (Groq Cloud LLM / Vision) or 'gemini' (Google Gemini)"
    )
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Groq API Key (from console.groq.com)"
    )
    GROQ_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model (e.g. llama-3.3-70b-versatile or llama-3.2-11b-vision-preview)"
    )
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API Key for AI-powered OCR, visual understanding & Persian text restoration"
    )
    AI_MODEL_NAME: str = Field(
        default="gemini-3.8-flash",
        description="Gemini model for Persian multimodal document extraction"
    )
    USE_AI_ENGINE: bool = Field(
        default=True,
        description="Enable AI-powered Persian document understanding in background worker"
    )

    # OCR Settings
    TESSERACT_LANG: str = Field(
        default="fas+eng",
        description="Tesseract language models (Farsi + English)"
    )
    TESSERACT_CMD: str = Field(
        default="/usr/bin/tesseract",
        description="Path to Tesseract OCR binary executable"
    )
    OCR_DPI: int = Field(
        default=300,
        description="Resolution DPI for rasterizing PDF pages for OCR"
    )

    # Production Webhook Configuration (Optional - falls back to Long Polling if empty)
    WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="HTTPS public URL for Telegram Webhook"
    )
    WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Secret token to validate incoming Telegram webhook requests"
    )
    PORT: int = Field(
        default=3000,
        description="Port for Webhook server"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Application logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Returns max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
