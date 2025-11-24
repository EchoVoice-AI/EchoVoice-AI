"""Configuration helpers."""
import os


def get_env(name: str, default=None):
    """Get an environment variable with an optional default."""
    return os.environ.get(name, default)
