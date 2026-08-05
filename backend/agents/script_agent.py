"""Script Generation Agent for Bangla YouTube Videos."""

import json
from typing import Any

from agents.base import BaseAgent
from utils.logger import get_logger

logger = get_logger()

SCRIPT_SYSTEM_PROMPT = """You are a professional YouTube scriptwriter for a Bangla tech channel. Your scripts are engaging, educational, and optimized for viewer retention.

SCRIPT STRUCTURE:
1. HOOK (0-5 sec): Attention-grabbing Bengali opening
2. INTRO (5-15 sec): What the viewer will learn
3. BODY (15-45 sec): Main content with clear explanations
4. OUTRO (45-60 sec): Summary and CTA (subscribe, like, comment)

RULES:
- Write in conversational Bengali (চলিত বাংলা)
- Keep sentences short and punchy
- Add emotion markers [উত্তেজিত], [গুরুত্বপূর্ণ], [মজার]
- Add visual cues for editors: [IMAGE: description], [TEXT: title]
- Include timestamps for each section
- For shorts: target 55-60 seconds total
- For long videos: target the requested duration

Return as JSON:
{
  "title": "Bengali title here",
  "script_bn": "Full Bengali script here...",
  "hooks": ["hook1", "hook2", "hook3"],
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
