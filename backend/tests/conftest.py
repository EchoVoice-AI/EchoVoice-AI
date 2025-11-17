import os
import sys


def pytest_configure():
    # Ensure the `backend` package directory is on sys.path so tests can import `app`.
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if base not in sys.path:
        sys.path.insert(0, base)
