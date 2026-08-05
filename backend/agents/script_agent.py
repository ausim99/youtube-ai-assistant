"""Script Generation Agent for Bangla YouTube Videos."""

import json
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()

SCRIPT_SYSTEM_PROMPT = """You are a professional YouTube scriptwriter for a Bangla tech channel. Create engaging, professional scripts that keep viewers watching.

SCRIPT STRUCTURE (Shorts ~55-60 seconds):
1. HOOK (0-5 sec): Powerful Bengali opening with number/statistic
2. INTRO (5-15 sec): Promise what viewer will learn
3. BODY (15-48 sec): 3-5 key points, each with clear text overlay
4. OUTRO (48-60 sec): CTA (subscribe, like, comment)

PROFESSIONAL TITLE FORMAT:
"ChatGPT দিয়ে ১০ মিনিটে ভিডিও বানান! (সিক্রেট ট্রিক)"
"AI দিয়ে মাসে ৫০,০০০ টাকা ইনকাম! (২০২৬ গোপন পদ্ধতি)"
"এই ৫টি AI টুল কেউ জানে না! 🤯"

RULES:
- Use natural conversational Bengali (চলিত বাংলা)
- Short punchy sentences (8-12 words max per line)
- Use power words: বিনামূল্যে, গোপন, সহজ, সেরা, নতুন, সম্পূর্ণ
- Include numbers and statistics
- Every 8-10 seconds introduce a new text overlay line
- Add visual cues: [TEXT: overlay text] at key moments
- Add emoji markers for emotion

TEXT OVERLAYS: Provide 6-8 short Bengali text overlay lines (appear one by one on screen)

Return JSON:
{
  "title": "SEO optimized Bangla title",
  "script_bn": "Full Bengali script for TTS...",
  "hooks": ["hook option 1", "hook option 2"],
  "text_overlays": ["Overlay 1", "Overlay 2", "Overlay 3", "Overlay 4", "Overlay 5", "Overlay 6"],
  "scenes": [{"timestamp": 0, "text": "...", "visual": "..."}],
  "duration_seconds": 60,
  "word_count": 150
}

IMPORTANT: Return ONLY valid JSON, no markdown or explanation."""


class ScriptAgent(BaseAgent):
    """Generates Bangla YouTube video scripts with hooks and scene descriptions."""

    async def execute(self, **kwargs) -> dict[str, Any]:
        idea_title = kwargs.get("idea_title", "")
        category = kwargs.get("category", "ai-tools")
        tone = kwargs.get("tone", "professional")
        duration_seconds = kwargs.get("duration_seconds", 60)

        prompt = f"""Write a YouTube video script in Bengali based on:
Title/Topic: {idea_title}
Category: {category}
Tone: {tone}
Target Duration: {duration_seconds} seconds
Language: Bengali (Bangla)

Make it highly engaging with a strong hook. Use everyday Bengali that anyone can understand.
Focus on practical value. The viewer should learn something actionable.

For shorts (under 60 seconds): fast-paced, hook-heavy.
For longer videos (3+ minutes): structured with clear sections.

Generate the complete script now."""

        logger.info(f"ScriptAgent: Generating script for '{idea_title}'")
        response = await self.generate(prompt, SCRIPT_SYSTEM_PROMPT)

        try:
            cleaned = response.strip()
            while cleaned.startswith("`"):
                idx = cleaned.find("\n")
                if idx == -1:
                    break
                cleaned = cleaned[idx + 1:].strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            if not cleaned.startswith("{"):
                start = cleaned.find("{")
                end = cleaned.rfind("}")
                if start != -1 and end != -1 and end > start:
                    cleaned = cleaned[start:end + 1]

            script = json.loads(cleaned)
            logger.info(f"ScriptAgent: Generated {script.get('word_count', 0)} word script")
            print(f"  Script: {script.get('title', 'N/A')[:60]}", flush=True)
            return script
        except json.JSONDecodeError as e:
            logger.error(f"ScriptAgent: Failed to parse response: {e}")
            print(f"  Raw response (first 300 chars): {response[:300]}", flush=True)
            return {
                "title": idea_title,
                "script_bn": response[:2000],
                "hooks": [],
                "scenes": [],
                "duration_seconds": duration_seconds,
                "word_count": len(response.split()),
            }
