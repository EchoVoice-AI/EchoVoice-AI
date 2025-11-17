"""Tracing helper for LangSmith integration.

This module creates a single `tracer` object that can be imported
throughout the app. If the `langchain`/`langsmith` tracer class is not
available, `tracer` will be `None` and callers should pass callbacks
only when `tracer` is not None.

Usage:
    from app.tracing import tracer
    if tracer:
        llm = OpenAI(..., callbacks=[tracer])
"""
import os

try:
    # LangChain v1 tracer for LangSmith
    from langchain.callbacks.tracers import LangSmithTracer

    # Instantiate tracer; LangSmithTracer will read `LANGSMITH_API_KEY`
    # from the environment when sending runs to the LangSmith service.
    tracer = LangSmithTracer()
except Exception:
    # If langchain/langsmith packages are not present, fall back to None.
    tracer = None

__all__ = ["tracer"]
