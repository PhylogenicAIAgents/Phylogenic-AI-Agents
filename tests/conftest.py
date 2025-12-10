"""Pytest configuration and fixtures for Allele testing."""

import pytest
import asyncio
import aiohttp
import os
from typing import List, Optional


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ollama_available_models() -> List[str]:
    """Get available Ollama models, pulling missing ones if needed."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return [model.get("name", "") for model in data.get("models", [])]
    except Exception:
        pass
    return []


@pytest.fixture(scope="session")
async def ensure_gemma_models(ollama_available_models):
    """Ensure gemma models are available, trying to pull if needed."""
    desired_models = ["gemma3:1b", "gemma2:2b", "gemma:latest"]
    available = ollama_available_models

    for model in desired_models:
        if model in available:
            return model  # Found exact gemma variant

    # Check for gemma prefix matches
    for model in available:
        if model.startswith("gemma"):
            return model  # Found some gemma variant

    # Try to pull gemma2:2b as it's most likely to exist
    fallback_model = "gemma2:2b"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/pull",
                json={"name": fallback_model},
                timeout=aiohttp.ClientTimeout(total=120)  # 2 minute timeout for pulling
            ) as response:
                if response.status == 200:
                    # Pull successful
                    return fallback_model
    except Exception:
        pass

    # Fall back to available models if gemma pull failed
    if "llama2:latest" in ollama_available_models:
        return "llama2:latest"
    if tinyllama_available := [m for m in ollama_available_models if "tinyllama" in m]:
        return tinyllama_available[0]

    return None  # No suitable model available


@pytest.fixture
def skip_if_cloud_models_unavailable():
    """Skip test if cloud models are not configured."""
    cloud_api_key = os.getenv("OLLAMA_API_KEY", "")

    # Basic check - if no key is set, assume cloud not configured
    if not cloud_api_key:
        pytest.skip("Cloud models not configured (no OLLAMA_API_KEY)")


@pytest.fixture
async def local_ollama_config(ensure_gemma_models):
    """Configuration for local Ollama testing."""
    gemma_model = ensure_gemma_models
    if gemma_model and isinstance(gemma_model, str):
        from allele.agent import AgentConfig
        return AgentConfig(
            llm_provider="ollama",
            model_name=gemma_model,
            api_key="",  # Ollama doesn't require API key
            temperature=0.1,  # Low creativity for predictable testing
            request_timeout=30
        )
    else:
        pytest.skip("No gemma models available locally and could not pull")


@pytest.fixture
def mock_genome():
    """Create a test genome for consistent testing."""
    from allele.genome import ConversationalGenome
    return ConversationalGenome(
        genome_id="test_genome",
        traits={
            'empathy': 0.8,
            'engagement': 0.7,
            'technical_knowledge': 0.6,
            'creativity': 0.9,
            'conciseness': 0.5,
            'context_awareness': 0.8,
            'adaptability': 0.7,
            'personability': 0.8
        }
    )
