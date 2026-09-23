import os
from sourcex.config import config

def test_config_loads():
    # Verify that the config module loads properly and the class is instantiated
    assert hasattr(config, 'GEMINI_API_KEY')
    
    # In the testing environment we might not have a real .env loaded,
    # but we can verify it safely handles missing/present variables.
    # The .env.example defines GEMINI_API_KEY as 'your_api_key_here'
    # If a real .env is not present, it will be None.
    # We just want to ensure it parses successfully without crashing.
    assert config.GEMINI_API_KEY is None or isinstance(config.GEMINI_API_KEY, str)
