import time
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.config import OLLAMA_BASE_URL, DEFAULT_MODEL

logger = logging.getLogger("travel_planner.ollama")

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama server is responding and list installed models."""
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                latency = round((time.time() - t0) * 1000, 1)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "online": True,
                        "latency_ms": latency,
                        "models": models,
                        "error": None
                    }
                return {
                    "online": False,
                    "latency_ms": latency,
                    "models": [],
                    "error": f"HTTP {res.status_code}"
                }
        except Exception as e:
            return {
                "online": False,
                "latency_ms": round((time.time() - t0) * 1000, 1),
                "models": [],
                "error": str(e)
            }

    async def get_models(self) -> List[str]:
        health = await self.check_health()
        return health.get("models", [])

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        json_format: bool = False,
        timeout: float = 240.0
    ) -> str:
        """Call Ollama /api/generate."""
        chosen_model = model or DEFAULT_MODEL
        payload: Dict[str, Any] = {
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_ctx": 8192
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_format:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text}")
                data = res.json()
                return data.get("response", "").strip()
        except httpx.ReadTimeout:
            raise RuntimeError(f"Ollama model '{chosen_model}' timed out after {int(timeout)}s. If this is the first run, the model might still be loading into GPU/RAM.")
        except httpx.ConnectError:
            raise RuntimeError(f"Could not connect to Ollama at {self.base_url}. Please ensure Ollama is running ('ollama serve').")
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise e

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        timeout: float = 120.0
    ) -> str:
        """Call Ollama /api/chat with full conversational history."""
        chosen_model = model or DEFAULT_MODEL
        payload = {
            "model": chosen_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "num_ctx": 8192
            }
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text}")
                data = res.json()
                msg = data.get("message", {})
                return msg.get("content", "").strip()
        except httpx.ReadTimeout:
            raise RuntimeError(f"Ollama model '{chosen_model}' timed out waiting for chat response.")
        except httpx.ConnectError:
            raise RuntimeError(f"Could not connect to Ollama at {self.base_url}. Is Ollama running?")
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise e

ollama_client = OllamaClient()
