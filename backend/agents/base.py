"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Any

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class BaseAgent(ABC):
    """Abstract base for all AI agents with retry and provider management."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.DEFAULT_AI_PROVIDER
        self._setup_provider()

    def _setup_provider(self):
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate text from the configured AI provider with retry logic."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
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
            logger.error(f"AI generation failed: {e}")
            raise

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Main execution method for the agent."""
        pass
