"""Configuration loader for external services."""
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. Defaults to config/services.yaml.
    
    Returns:
        Configuration dictionary with environment variable substitution.
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/services.yaml")
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Substitute environment variables
    config = _substitute_env_vars(config)
    
    return config


def _substitute_env_vars(obj: Any) -> Any:
    """Recursively substitute environment variables in config values.
    
    Supports ${VAR_NAME} syntax for environment variable substitution.
    """
    if isinstance(obj, str):
        if obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, "")
        return obj
    elif isinstance(obj, dict):
        return {k: _substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    return obj


def get_enabled_services(config: dict[str, Any], service_type: str) -> list[dict[str, Any]]:
    """Get list of enabled services for a given type.
    
    Args:
        config: Configuration dictionary.
        service_type: Type of service (plagiarism_checkers, ai_detectors, rephrasing).
    
    Returns:
        List of enabled service configurations.
    """
    services = config.get("services", {}).get(service_type, [])
    return [s for s in services if s.get("enabled", False)]


def get_openai_config(config: dict[str, Any]) -> dict[str, str]:
    """Get OpenAI configuration.
    
    Args:
        config: Configuration dictionary.
    
    Returns:
        OpenAI configuration with api_key and model.
    """
    openai_config = config.get("openai", {})
    return {
        "api_key": openai_config.get("api_key", os.getenv("OPENAI_API_KEY", "")),
        "model": openai_config.get("model", "gpt-4")
    }
