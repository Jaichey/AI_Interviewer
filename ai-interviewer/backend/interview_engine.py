import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import time
from datetime import datetime, timedelta
from pathlib import Path

import google.generativeai as genai
import requests
from dotenv import load_dotenv


class ModelRotator:
    """Manages automatic model rotation when quotas are reached."""
    
    # Models with their daily free tier limits (using Gemini 2.5 series)
    MODELS = [
        {"name": "gemini-2.5-flash", "daily_limit": 1500, "rpm": 15},
        {"name": "gemini-2.5-flash-lite", "daily_limit": 2000, "rpm": 20},
        {"name": "gemini-2.5-pro", "daily_limit": 50, "rpm": 2},
    ]
    
    def __init__(self):
        self.request_counts = {m["name"]: 0 for m in self.MODELS}
        self.last_reset = datetime.now()
        self.current_model_idx = 0
        self.rpm_tracker = {m["name"]: [] for m in self.MODELS}
        
    def get_current_model(self) -> str:
        """Get the current model to use, rotating if quota exceeded."""
        self._reset_daily_counts()
        
        # Check all models starting from current
        for i in range(len(self.MODELS)):
            idx = (self.current_model_idx + i) % len(self.MODELS)
            model = self.MODELS[idx]
            
            # Check daily limit
            if self.request_counts[model["name"]] >= model["daily_limit"] * 0.9:  # 90% threshold
                print(f"[MODEL ROTATION] {model['name']} near daily limit, trying next...")
                continue
                
            # Check RPM limit
            if not self._check_rpm_limit(model["name"], model["rpm"]):
                print(f"[MODEL ROTATION] {model['name']} RPM limit reached, trying next...")
                continue
                
            # Found available model
            if idx != self.current_model_idx:
                print(f"[MODEL ROTATION] Switched from {self.MODELS[self.current_model_idx]['name']} to {model['name']}")
                self.current_model_idx = idx
            
            return model["name"]
        
        # All models exhausted, use first and hope for the best
        print("[MODEL ROTATION] All models exhausted, using fallback")
        return self.MODELS[0]["name"]
    
    def _check_rpm_limit(self, model_name: str, rpm_limit: int) -> bool:
        """Check if we're within RPM (requests per minute) limit."""
        now = time.time()
        # Remove requests older than 1 minute
        self.rpm_tracker[model_name] = [t for t in self.rpm_tracker[model_name] if now - t < 60]
        return len(self.rpm_tracker[model_name]) < rpm_limit
    
    def record_request(self, model_name: str):
        """Record a request for rate limiting."""
        self.request_counts[model_name] += 1
        self.rpm_tracker[model_name].append(time.time())
        print(f"[MODEL STATS] {model_name}: {self.request_counts[model_name]} requests today")
    
    def _reset_daily_counts(self):
        """Reset counts if a new day has started."""
        now = datetime.now()
        if now - self.last_reset > timedelta(days=1):
            print("[MODEL ROTATION] Resetting daily counts")
            self.request_counts = {m["name"]: 0 for m in self.MODELS}
            self.last_reset = now

    def mark_quota_hit(self, model_name: str):
        """Mark a model as exhausted so rotation skips it next time."""
        for idx, model in enumerate(self.MODELS):
            if model["name"] == model_name:
                # Inflate counts to push the model out of rotation for this run
                self.request_counts[model_name] = model["daily_limit"] * 2
                self.current_model_idx = (idx + 1) % len(self.MODELS)
                break


# Global rotator instance
_model_rotator = ModelRotator()

# Load project-level environment variables so provider keys are available when
# interview_engine is imported directly (e.g., via uvicorn).
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


class ProviderQuotaExceeded(Exception):
    """Raised when a provider signals quota or rate limit issues."""


class ProviderUnavailable(Exception):
    """Raised when a provider fails for non-quota reasons."""


class InterviewEngine:
    """Interview engine wrapping Google Gemini API with automatic model rotation."""

    def __init__(self, system_prompt: str, model: Optional[str] = None, temperature: float = 0.55) -> None:
        self.system_prompt = system_prompt
        self.use_rotation = model is None  # Only rotate if no specific model requested
        self.fixed_model = model
        api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_enabled = bool(api_key)
        if self.gemini_enabled:
            genai.configure(api_key=api_key)
        else:
            print("[INIT] GEMINI_API_KEY not set; Gemini fallback will be skipped if reached")
        self.temperature = temperature
        self.provider_usage: Dict[str, int] = {}
        self.exhausted_providers: set[str] = set()

    async def generate(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Build prompt from message history for Gemini
        prompt_parts = [f"System: {self.system_prompt}\n"]
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}")
        prompt_parts.append("\nRespond with valid JSON only.")
        full_prompt = "\n".join(prompt_parts)
        
        content: Optional[str] = None
        providers = [
            "gemini",
            "groq",
            "openrouter",
            "huggingface",
            "cohere",
        ]

        for provider in providers:
            if provider in self.exhausted_providers:
                continue

            try:
                if provider == "gemini":
                    if not self.gemini_enabled:
                        raise ProviderUnavailable("Gemini not configured")
                    content = await self._call_gemini(full_prompt)
                elif provider == "groq":
                    content = await self._call_groq(full_prompt)
                elif provider == "openrouter":
                    content = await self._call_openrouter(full_prompt)
                elif provider == "huggingface":
                    content = await self._call_huggingface(full_prompt)
                elif provider == "cohere":
                    content = await self._call_cohere(full_prompt)
                else:
                    continue

                self.provider_usage[provider] = self.provider_usage.get(provider, 0) + 1
                if content:
                    break
            except ProviderQuotaExceeded as exc:
                print(f"[DEBUG] Provider {provider} quota/rate limit: {exc}")
                self.exhausted_providers.add(provider)
                continue
            except ProviderUnavailable as exc:
                print(f"[DEBUG] Provider {provider} unavailable: {exc}")
                self.exhausted_providers.add(provider)
                continue

        if content is None:
            return {
                "system_state": "COMPLETED",
                "interviewer_response": "Thank you for your time today. We've reached our system capacity for now. Your responses were great, and we'd love to continue this conversation later. Please feel free to reach out again!",
                "avatar_state": "smiling",
                "tts_enabled": True,
                "ui_mode": "professional_minimal",
                "next_action": "end_interview",
            }

        try:
            # Try to extract JSON from response (in case there's text before/after)
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)
            else:
                parsed = json.loads(content)
            print(f"[DEBUG] Successfully parsed JSON")
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if JSON parsing fails
            print(f"[DEBUG] JSON parse failed: {e}, using fallback")
            parsed = {}

        required_keys = {
            "system_state",
            "interviewer_response",
            "avatar_state",
            "tts_enabled",
            "ui_mode",
            "next_action",
        }
        defaults = {
            "system_state": "WARM_UP",
            "interviewer_response": content[:200] if content else "Tell me about yourself.",
            "avatar_state": "neutral_listening",
            "tts_enabled": True,
            "ui_mode": "professional_minimal",
            "next_action": "wait_for_user_answer",
        }
        for key, value in defaults.items():
            parsed.setdefault(key, value)
        # Ensure required keys exist even if parsed empty
        for key in required_keys:
            parsed.setdefault(key, defaults.get(key, ""))
        return parsed

    def _ensure_api_key(self, env_var: str) -> str:
        value = os.getenv(env_var)
        if not value:
            raise ProviderUnavailable(f"{env_var} not set")
        return value

    def _is_quota_message(self, text: str) -> bool:
        lowered = text.lower()
        return "quota" in lowered or "rate limit" in lowered or "429" in lowered

    async def _call_gemini(self, prompt: str) -> str:
        attempted_models = set()
        max_attempts = len(_model_rotator.MODELS) if self.use_rotation else 1
        loop = asyncio.get_event_loop()

        for _ in range(max_attempts):
            model_name = (
                _model_rotator.get_current_model()
                if self.use_rotation
                else self.fixed_model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            )
            attempted_models.add(model_name)

            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: genai.GenerativeModel(model_name).generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(temperature=self.temperature),
                    ),
                )
                text = response.text or "{}"
                print(f"[DEBUG] Gemini ({model_name}) raw response: {text[:300]}")
                if self.use_rotation:
                    _model_rotator.record_request(model_name)
                return text
            except Exception as exc:
                print(f"[DEBUG] Gemini call failed with {model_name}: {exc}")
                if self.use_rotation and self._is_quota_message(str(exc)):
                    _model_rotator.mark_quota_hit(model_name)
                    if len(attempted_models) >= max_attempts:
                        raise ProviderQuotaExceeded("Gemini quota exhausted")
                    await asyncio.sleep(0.5)
                    continue
                if "404" in str(exc):
                    raise ProviderUnavailable("Gemini model not found")
                raise ProviderUnavailable(str(exc))

        raise ProviderQuotaExceeded("Gemini quota exhausted")

    async def _call_groq(self, prompt: str) -> str:
        api_key = self._ensure_api_key("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        loop = asyncio.get_event_loop()

        def _call() -> str:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": self.temperature}
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=20)
            if resp.status_code == 429 or self._is_quota_message(resp.text):
                raise ProviderQuotaExceeded("Groq quota")
            if resp.status_code >= 400:
                raise ProviderUnavailable(f"Groq {resp.status_code}")
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        return await loop.run_in_executor(None, _call)

    async def _call_openrouter(self, prompt: str) -> str:
        api_key = self._ensure_api_key("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528:free")
        loop = asyncio.get_event_loop()

        def _call() -> str:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": self.temperature}
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=20)
            if resp.status_code == 429 or self._is_quota_message(resp.text):
                raise ProviderQuotaExceeded("OpenRouter quota")
            if resp.status_code >= 400:
                raise ProviderUnavailable(f"OpenRouter {resp.status_code}")
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        return await loop.run_in_executor(None, _call)

    async def _call_huggingface(self, prompt: str) -> str:
        api_key = self._ensure_api_key("HUGGINGFACE_API_KEY")
        model = os.getenv("HUGGINGFACE_MODEL", "tiiuae/falcon-7b-instruct")
        loop = asyncio.get_event_loop()

        def _call() -> str:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {"inputs": prompt, "parameters": {"max_new_tokens": 512, "return_full_text": False}}
            url = f"https://api-inference.huggingface.co/models/{model}"
            resp = requests.post(url, headers=headers, json=body, timeout=20)
            if resp.status_code == 429 or self._is_quota_message(resp.text):
                raise ProviderQuotaExceeded("HuggingFace quota")
            if resp.status_code >= 400:
                raise ProviderUnavailable(f"HuggingFace {resp.status_code}")
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "{}")
            return data.get("generated_text", "{}") if isinstance(data, dict) else "{}"

        return await loop.run_in_executor(None, _call)

    async def _call_cohere(self, prompt: str) -> str:
        api_key = self._ensure_api_key("COHERE_API_KEY")
        model = os.getenv("COHERE_MODEL", "command-r")
        loop = asyncio.get_event_loop()

        def _call() -> str:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            body = {"model": model, "message": prompt, "temperature": self.temperature}
            resp = requests.post("https://api.cohere.com/v1/chat", headers=headers, json=body, timeout=20)
            if resp.status_code == 429 or self._is_quota_message(resp.text):
                raise ProviderQuotaExceeded("Cohere quota")
            if resp.status_code >= 400:
                raise ProviderUnavailable(f"Cohere {resp.status_code}")
            data = resp.json()
            return data.get("text") or data.get("response", {}).get("text", "{}")

        return await loop.run_in_executor(None, _call)

    async def run_turn(self, user_text: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            *history,
            {"role": "user", "content": user_text},
        ]
        return await self.generate(messages)


class MockInterviewEngine(InterviewEngine):
    """Lightweight mock for tests."""

    def __init__(self) -> None:
        self.system_prompt = "mock"
        self.use_rotation = False
        self.fixed_model = "mock"
        self.temperature = 0.0

    async def generate(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:  # type: ignore[override]
        await asyncio.sleep(0)
        return {
            "system_state": "TECHNICAL",
            "interviewer_response": "Test question: What is your stack?",
            "avatar_state": "neutral_listening",
            "tts_enabled": True,
            "ui_mode": "professional_minimal",
            "next_action": "wait_for_user_answer",
        }
