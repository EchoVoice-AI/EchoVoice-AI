"""Shared utilities used by route modules (JSON encoder, NDJSON streamer)."""
import json
from collections.abc import AsyncGenerator


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for dataclasses and other types used by approaches."""

    def default(self, o):
        try:
            from dataclasses import asdict, is_dataclass

            if is_dataclass(o) and not isinstance(o, type):
                as_dict = asdict(o)
                if isinstance(as_dict, dict):
                    return {k: v for k, v in as_dict.items() if v is not None}
                return as_dict
        except Exception:
            pass
        return super().default(o)


async def ndjson_bytes(generator: AsyncGenerator[dict, None]):
    """Encode events from an async generator as NDJSON bytes."""
    try:
        async for event in generator:
            yield (json.dumps(event, ensure_ascii=False, cls=JSONEncoder) + "\n").encode("utf-8")
    except Exception as exc:
        yield (json.dumps({"error": str(exc)}) + "\n").encode("utf-8")
