import os
import sys


def pytest_configure():
    # Ensure the repository root (parent of `backend`) is on sys.path so tests
    # can import packages like `backend.services` or `app` reliably. Previously
    # we inserted the `backend` directory which made `import backend...` fail
    # (Python would look for backend/backend). Add the repo root instead.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
