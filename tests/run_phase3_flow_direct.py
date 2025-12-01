import asyncio
import importlib.util
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `PersonalizeAI` package can be imported
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

spec = importlib.util.spec_from_file_location("test_phase3_flow", Path(__file__).parent / "test_phase3_flow.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

test_coro = getattr(mod, "test_phase3_compliance_loop_with_llm")


if __name__ == "__main__":
    asyncio.run(test_coro())
