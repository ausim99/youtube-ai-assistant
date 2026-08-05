"""SEO Agent - Generates titles, descriptions, tags, and hashtags for YouTube."""

import json
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()

SEO_SYSTEM_PROMPT = """You are an expert YouTube SEO strategist specializing in Bangla content. You optimize videos for maximum reach in Bengali-speaking audiences.

For the given video topic/script, generate:
1. 3 SEO-optimized Bangla titles (different angles)
2. YouTube description (Bangla, 200+ words with keywords)
3. 15-20 relevant tags (mix of Bangla and English)
4. 10 hashtags (Bangla focused)
5. Video chapters/timestamps
6. Thumbnail text suggestion (3-5 Bangla words, high CTR)
7. Pinned comment (Bangla, engaging)
8. Community post text (Bangla)

CRITICAL SEO RULES:
- Primary keyword in the first 25 characters of title
- Description must have keywords in first 2-3 lines (above fold)
- Use high-volume Bangla search terms
- Mix broad and long-tail keywords
- Power words in titles: বিনামূল্যে, সহজ, সেরা, গোপন, নতুন, সম্পূর্ণ

Return as valid JSON."""


class SEOAgent(BaseAgent):
    """Generates YouTube SEO metadata optimized for Bangla audience."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        title = kwargs.get("title", "")
        script = kwargs.get("script", "")
        category = kwargs.get("category", "ai-tools")
        keywords = kwargs.get("keywords", [])

        prompt = f"""Generate complete YouTube SEO metadata for:
Video Title: {title}
Category: {category}
Target Keywords: {', '.join(keywords) if keywords else 'AI, tech, Bangla'}
Script Preview: {script[:500]}

Optimize for:
- Bangla-speaking audience (Bangladesh + West Bengal)
- High search volume Bangla keywords
- YouTube algorithm ranking factors
- Click-through rate optimization

Generate ALL fields as JSON."""

        logger.info(f"SEOAgent: Generating SEO metadata for '{title}'")
        response = await self.generate(prompt, SEO_SYSTEM_PROMPT)

        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            seo_data = json.loads(cleaned)
            logger.info(f"SEOAgent: Generated SEO with {len(seo_data.get('tags', []))} tags")
            return seo_data
        except json.JSONDecodeError:
            logger.warning("SEOAgent: Failed to parse JSON, returning raw structure")
            return {
                "titles": [title],
                "description": script[:1000],
                "tags": ["AI", "Bangla", "Tech", category],
                "hashtags": ["#AI", "#Bangla", "#Tech"],
                "chapters": [],
                "thumbnail_text": "নতুন AI টুল",
                "pinned_comment": "ভিডিওটি কেমন লাগলো জানাবেন!",
                "community_post": "নতুন ভিডিও আপলোড করা হয়েছে!",
            }
