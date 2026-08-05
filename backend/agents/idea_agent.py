"""Content Idea Generation Agent for Bangla YouTube Content."""

import json
from datetime import datetime
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()

CATEGORIES = [
    "ai-tools", "chatgpt", "claude", "gemini", "prompt-engineering",
    "automation", "python", "ai-agents", "tech-news", "productivity",
    "business-ai", "seo", "coding", "trending-ai",
]

IDEA_SYSTEM_PROMPT = """You are an expert YouTube content strategist for a Bangla-language AI/tech channel.

Your task is to generate unique, high-CTR content ideas in Bengali for AI, tech, and productivity content.

For each idea, provide:
1. Title in Bengali (catchy, click-inducing)
2. Title in English
3. Category
4. Hook (first 3 seconds script in Bengali)
5. Unique angle (why this video is different)
6. Target audience
7. Difficulty level (easy/medium/hard)
8. Expected CTR (0-100)
9. Expected RPM (in USD)
10. Expected views

Return as a valid JSON array of objects. Each object must have ALL fields.
Use Bengali language for titles, hooks, and audience descriptions.

IMPORTANT: Return ONLY the JSON array, no markdown, no explanation."""


class IdeaAgent(BaseAgent):
    """Generates daily Bangla content ideas with trend analysis."""

    async def execute(self, **kwargs) -> list[dict[str, Any]]:
        category = kwargs.get("category", "ai-tools")
        count = kwargs.get("count", 5)
        language = kwargs.get("language", "bn")

        prompt = f"""Generate {count} unique YouTube video ideas for a Bangla tech channel.
Category: {category}
Language: Bengali (bn)
Focus on topics that are currently trending and have high search volume in Bangladesh and West Bengal.

Make sure the titles are optimized for Bangla YouTube search.
Focus on practical, actionable, and curiosity-driven content.
Today's date: {datetime.now().strftime('%Y-%m-%d')}"""

        logger.info(f"IdeaAgent: Generating {count} ideas for category {category}")
        response = await self.generate(prompt, IDEA_SYSTEM_PROMPT)

        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            ideas = json.loads(cleaned)
            logger.info(f"IdeaAgent: Generated {len(ideas)} ideas")
            return ideas
        except json.JSONDecodeError as e:
            logger.error(f"IdeaAgent: Failed to parse response: {e}")
            logger.error(f"Raw response: {response[:500]}")
            return []
