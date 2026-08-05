"""Base agent class for all AI agents."""

import re
import time
from abc import ABC, abstractmethod
from typing import Any

import google.generativeai as genai

from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()

MAX_RETRIES = 5
RETRY_DELAY_BASE = 10


def parse_retry_delay(error_message: str) -> int:
    """Extract retry delay in seconds from Gemini rate-limit error."""
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_message)
    if match:
        return int(float(match.group(1))) + 2
    return RETRY_DELAY_BASE


class BaseAgent(ABC):
    """Abstract base for all AI agents with retry and provider management."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.DEFAULT_AI_PROVIDER
        self.model = None
        self._setup_provider()

    def _setup_provider(self):
        self.model = None
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        elif self.provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )
            self.model = "deepseek-chat"
        elif self.provider == "grok" and settings.GROK_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=settings.GROK_API_KEY,
                base_url="https://api.x.ai/v1",
            )
            self.model = "grok-2-latest"
        if not self.model:
            logger.warning(f"BaseAgent: No AI provider configured for {self.provider}. Set API keys.")

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate text from the configured AI provider with rate-limit aware retry."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if self.provider == "gemini":
                    response = await self.model.generate_content_async(full_prompt)
                    return response.text
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt or ""},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=4096,
                    )
                    return response.choices[0].message.content

            except Exception as e:
                last_error = e
                error_str = str(e)
                delay = parse_retry_delay(error_str)
                is_rate_limit = "429" in error_str or "quota" in error_str.lower()

                if attempt < MAX_RETRIES:
                    if is_rate_limit:
                        logger.warning(f"Rate limited (attempt {attempt}/{MAX_RETRIES}), waiting {delay}s...")
                        print(f"  Rate limited, waiting {delay}s before retry {attempt + 1}/{MAX_RETRIES}...", flush=True)
                    else:
                        delay = min(delay * attempt, 60)
                        logger.warning(f"AI error (attempt {attempt}/{MAX_RETRIES}): {e}, retrying in {delay}s...")
                        print(f"  Error, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})...", flush=True)

                    await self._sleep(delay)
                else:
                    logger.error(f"AI generation failed after {MAX_RETRIES} attempts: {e}")

        raise last_error

    async def _sleep(self, seconds: int):
        """Async sleep for the given duration."""
        import asyncio
        await asyncio.sleep(seconds)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Main execution method for the agent."""
        pass
