import json
import os
import urllib.error
import urllib.request

from app.models import Persona


class AIError(Exception):
    pass


def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIError("OPENAI_API_KEY is not configured. Set it in your .env file or environment.")
    return api_key


def build_caption_prompt(persona: Persona, prompt: str | None = None) -> str:
    instructions = [
        "Write a ready-to-post Instagram caption.",
        "Keep the caption engaging, on-brand, and concise.",
        "Include 3-5 relevant hashtags at the end.",
    ]

    if persona.niche:
        instructions.append(f"Persona niche: {persona.niche}.")
    if persona.bio:
        instructions.append(f"Persona bio: {persona.bio}.")
    if persona.caption_tone:
        instructions.append(f"Caption tone: {persona.caption_tone}.")
    if persona.personality:
        instructions.append(f"Personality notes: {persona.personality}.")
    if persona.visual_style:
        instructions.append(f"Visual style: {persona.visual_style}.")

    if prompt:
        instructions.append(f"Use this prompt: {prompt}.")
    else:
        instructions.append("Write a caption that fits this persona and their audience.")

    instructions.append("Do not include any code blocks or markdown formatting.")
    return " ".join(instructions)


def generate_caption(persona: Persona, prompt: str | None = None, max_tokens: int = 220) -> str:
    api_key = get_openai_api_key()
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    api_url = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a creative social media copywriter for Instagram."},
            {"role": "user", "content": build_caption_prompt(persona, prompt)},
        ],
        "temperature": 0.8,
        "max_tokens": max_tokens,
        "n": 1,
    }

    request_body = json.dumps(data).encode("utf-8")
    request_url = f"{api_url.rstrip('/')}/chat/completions"
    request = urllib.request.Request(
        request_url,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise AIError(f"OpenAI API request failed: {detail}") from exc
    except Exception as exc:
        raise AIError(f"OpenAI API request failed: {exc}") from exc

    choices = payload.get("choices")
    if not choices:
        raise AIError("OpenAI API returned no completion choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if not content:
        raise AIError("OpenAI API returned an empty caption.")

    return content.strip()
