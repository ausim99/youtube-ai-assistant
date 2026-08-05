"""Base agent class for all AI agents with multi-provider fallback."""

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Any

import google.generativeai as genai

from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

# Provider priority: try them in this order
PROVIDER_ORDER = ["gemini", "deepseek", "grok"]

RETRY_DELAY_BASE = 10
MAX_PER_PROVIDER_RETRIES = 2


def parse_retry_delay(error_message: str) -> int:
    """Extract retry delay in seconds from rate-limit error."""
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_message)
    if match:
        return int(float(match.group(1))) + 2
    return RETRY_DELAY_BASE


def get_available_providers() -> list[str]:
    """Return ordered list of providers that have API keys configured."""
    providers = []
    if settings.GEMINI_API_KEY:
        providers.append("gemini")
    if settings.DEEPSEEK_API_KEY:
        providers.append("deepseek")
    if settings.GROK_API_KEY:
        providers.append("grok")
    return providers if providers else ["gemini"]


class BaseAgent(ABC):
    """Abstract base for all AI agents with automatic multi-provider fallback."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.DEFAULT_AI_PROVIDER
        self.model = None
        self.client = None
        self.current_provider = None
        self._setup_provider(self.provider)

    def _setup_provider(self, provider: str):
        """Configure a specific provider."""
        self.current_provider = provider
        self.model = None
        self.client = None

        if provider == "gemini" and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-2.0-flash")

        elif provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )
            self.model = "deepseek-chat"

        elif provider == "grok" and settings.GROK_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=settings.GROK_API_KEY,
                base_url="https://api.x.ai/v1",
            )
            self.model = "grok-2-latest"

        if not self.model and not self.client:
            logger.warning(f"BaseAgent: Provider '{provider}' not configured. Missing API key.")

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate text with automatic provider fallback on rate limit / failure."""
        providers = get_available_providers()
        if not providers:
            raise RuntimeError("No AI providers configured. Set GEMINI_API_KEY, DEEPSEEK_API_KEY, or GROK_API_KEY.")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        last_error = None

        for provider in providers:
            self._setup_provider(provider)
            print(f"  Trying provider: {provider}", flush=True)
            logger.info(f"BaseAgent: Trying provider {provider}")

            for attempt in range(1, MAX_PER_PROVIDER_RETRIES + 1):
                try:
                    result = await self._call_provider(full_prompt, system_prompt)
                    if result:
                        print(f"  Success with {provider}", flush=True)
                        self.current_provider = provider
                        return result

                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    is_rate_limit = "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower()

                    if is_rate_limit:
                        delay = parse_retry_delay(error_str)
                        logger.warning(f"{provider} rate limited (attempt {attempt}/{MAX_PER_PROVIDER_RETRIES})")
                        print(f"  {provider}: rate limited, switching provider...", flush=True)
                        break  # Don't retry same provider on rate limit, fall back to next

                    if attempt < MAX_PER_PROVIDER_RETRIES:
                        delay = min(RETRY_DELAY_BASE * attempt, 30)
                        logger.warning(f"{provider} error (attempt {attempt}): {e}")
                        print(f"  {provider}: error, retrying in {delay}s...", flush=True)
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"{provider} failed after {MAX_PER_PROVIDER_RETRIES} attempts")
                        print(f"  {provider}: failed, switching...", flush=True)

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def _call_provider(self, full_prompt: str, system_prompt: str | None) -> str:
        """Make the actual API call to the current provider."""
        if self.current_provider == "gemini" and self.model:
            response = await self.model.generate_content_async(full_prompt)
            return response.text

        elif self.current_provider in ("deepseek", "grok") and self.client:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt or ""},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content

        return None

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Main execution method for the agent."""
        pass
