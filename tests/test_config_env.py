import os

from allele import settings


def test_env_override_agent_model():
    # Set env var to change AGENT model name
    os.environ['AGENT__MODEL_NAME'] = 'test-model-env'

    # Recreate settings to pick up environment change
    from allele.config import AlleleSettings
    config = AlleleSettings()

    assert config.agent.model_name == 'test-model-env'

    # Cleanup
    del os.environ['AGENT__MODEL_NAME']
