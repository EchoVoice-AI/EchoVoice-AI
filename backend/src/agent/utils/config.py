"""Configuration helpers"""
import os


def get_env(name: str, default=None):
    return os.environ.get(name, default)
