# LLM Integration Guide

## Overview

The Allele SDK now includes production-ready Large Language Model (LLM) integration, enabling real conversational AI with genome-based personality traits.

## Quick Start

```python
from allele import ConversationalGenome, AgentConfig, NLPAgent
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# Create genome with personality traits
genome = ConversationalGenome("empathetic_agent", {
    'empathy': 0.9,          # Highly empathetic
    'engagement': 0.8,       # Very engaging
    'technical_knowledge': 0.7,  # Good technical knowledge
    'creativity': 0.8,       # Creative
})

# Configure agent
config = AgentConfig(
    llm_provider="openai",
    model_name="gpt-4-turbo",
    temperature=0.7,
    fallback_to_mock=False
)

# Create and initialize agent
agent = NLPAgent(genome, config)
await agent.initialize()

# Start conversation
async for response in agent.chat("I'm feeling stressed about my project"):
    print(response, end='')
```

## Configuration

### Environment Variables

```bash
# Set in your .env file or environment
OPENAI_API_KEY=sk-your-api-key-here
```

### Agent Configuration

```python
from allele import AgentConfig

config = AgentConfig(
    # LLM Provider
    llm_provider="openai",  # 'openai' or 'anthropic'

    # Model Selection
    model_name="gpt-4-turbo",  # or 'gpt-4', 'gpt-3.5-turbo', etc.

    # Generation Parameters
    temperature=0.7,        # 0.0-2.0: creativity vs consistency
    max_tokens=2048,        # Maximum response length

    # Streaming & Performance
    streaming=True,         # Enable streaming responses
    request_timeout=60,     # Request timeout in seconds

    # Rate Limiting
    rate_limit_requests_per_minute=60,
    rate_limit_tokens_per_minute=10000,

    # Conversation Management
    conversation_memory=50,    # Messages to keep in history
    context_window=10,         # Recent messages for context
    max_context_length=8000,   # Approximate token limit

    # Reliability
    max_retry_attempts=3,     # Retry failed requests
    fallback_to_mock=False,   # Fallback behavior
)
```

## Supported Providers

### OpenAI
```python
config = AgentConfig(llm_provider="openai", model_name="gpt-4-turbo")
# Supports: gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-4o, gpt-4o-mini
```

### Anthropic (Future)
```python
config = AgentConfig(llm_provider="anthropic", model_name="claude-3-opus-20240229")
# Coming soon...
```

## Genome-Based Personalization

The agent creates dynamic system prompts based on genome traits:

```python
genome = ConversationalGenome("tech_support", {
    'empathy': 0.8,
    'technical_knowledge': 0.9,
    'conciseness': 0.7,
    'context_awareness': 0.8,
})
```

This generates a prompt like:

> You are an AI assistant with these personality traits:
> - emotional understanding and compassionate responses (0.8/1.0)
> - depth of technical expertise and accuracy (0.9/1.0)
> - balancing completeness with brevity (0.7/1.0)
> - understanding conversation history and maintaining continuity (0.8/1.0)
>
> Your genome ID: tech_support
> Current generation: 0
>
> Respond naturally while embodying these traits in your communication style.

## Error Handling

### Automatic Retries
The integration includes exponential backoff for transient failures:
- Rate limit errors
- Network timeouts
- Temporary server errors

### Fallback Mode
Enable fallback for development/testing:

```python
config = AgentConfig(fallback_to_mock=True)
# Returns template responses instead of failing
```

### Exception Types
- `LLMAuthenticationError`: Invalid API credentials
- `LLMRateLimitError`: API rate limiting
- `LLMGenerationError`: Model generation failures
- `LLMTimeoutError`: Request timeouts
- `LLMQuotaExceededError`: Billing/account limits

## Monitoring & Metrics

Access comprehensive metrics after conversations:

```python
metrics = await agent.get_metrics()

print(f"Total requests: {metrics['performance']['total_requests']}")
print(f"Error rate: {metrics['performance']['error_rate']}")
print(f"Total cost: ${metrics['llm']['cost']}")
print(f"Average latency: {metrics['performance']['average_latency_ms']}ms")
```

## Conversation History

The agent maintains conversation history automatically:

```python
history = await agent.get_conversation_history()
for turn in history:
    print(f"User: {turn['user_input']}")
    print(f"Agent: {turn['agent_response']}")

# Reset conversation
await agent.reset_conversation()
```

## Testing

### Unit Tests
```bash
# Run LLM integration tests only
pytest tests/test_llm_integration.py -v
```

### With Real API
```bash
# Set API key and run
export OPENAI_API_KEY=sk-your-key
pytest tests/test_llm_integration.py::TestLLMIntegration::test_chat_with_real_api -v
```

### Mock Testing
```python
# Test without API key using fallbacks
config = AgentConfig(fallback_to_mock=True)
agent = NLPAgent(genome, config)
```

## Performance Optimization

### Rate Limiting
Automatic rate limiting prevents API quota exhaustion:

```python
# Customize rate limits
config = AgentConfig(
    rate_limit_requests_per_minute=30,  # Lower for development
    rate_limit_tokens_per_minute=5000   # Match your API tier
)
```

### Context Management
Intelligent context truncation:
- Maintains conversation continuity
- Prevents token limit errors
- Preserves recent relevant history

### Cost Optimization
- Automatic cost tracking per conversation
- Token usage monitoring
- Estimate costs before sending requests

## Troubleshooting

### Common Issues

**API Key Not Found**
```python
# Option 1: Environment variable
export OPENAI_API_KEY=sk-your-key

# Option 2: Direct configuration
config = AgentConfig(api_key="sk-your-key")
```

**Rate Limiting**
```python
# Reduce rate limits
config = AgentConfig(
    rate_limit_requests_per_minute=10,
    rate_limit_tokens_per_minute=1000
)
```

**Timeout Errors**
```python
# Increase timeout
config = AgentConfig(request_timeout=120)
```

### Logging
```python
# Enable debug logging
import logging
logging.getLogger('allele.llm_client').setLevel(logging.DEBUG)
```

## Advanced Usage

### Custom System Prompts
```python
config = AgentConfig(
    system_prompt_template="""
    You are a {genome_id} with special expertise in {custom_field}.
    {trait_descriptions}
    Always be helpful and maintain conversation flow.
    """
)
```

### Multiple Agents
```python
# Create different agents with different traits
support_agent = NLPAgent(support_genome, config)
sales_agent = NLPAgent(sales_genome, config)

# Handle different conversation types
if topic == "support":
    response = support_agent.chat(message)
else:
    response = sales_agent.chat(message)
```

### Health Monitoring
```python
health = await agent.llm_client.get_health_status()
print(f"Provider: {health['provider']}")
print(f"Errors: {health['error_rate']}")
print(f"Uptime: {health['uptime_seconds']}s")
```

## API Reference

### Classes
- `AgentConfig`: Agent configuration with LLM settings
- `NLPAgent`: Main conversational agent class
- `OpenAIClient`: OpenAI API client wrapper
- `LLMClient`: Abstract base class for all LLM providers

### Exceptions
- `LLMError`: Base LLM exception
- `LLMAuthenticationError`: Authentication failures
- `LLMRateLimitError`: Rate limiting
- `LLMGenerationError`: Generation failures
- `LLMTimeoutError`: Timeout errors
- `LLMQuotaExceededError`: Quota exceedance

For complete API documentation, see the docstrings in each module.
