"""kit.mcp – Model Context Protocol server wrapper."""

from __future__ import annotations

# No longer need importlib for lazy loading
# from importlib import import_module

from .main import main as main  # main is still fine
from .server import serve as serve # Directly import serve

# Remove __getattr__ and _load_serve for lazy loading
# def _load_serve():  # type: ignore
#     return import_module("kit.mcp.server").serve
#
# def __getattr__(name: str):  # noqa: D401
#     if name == "serve":
#         serve = _load_serve()
#         globals()["serve"] = serve
#         return serve
#     raise AttributeError(name)

__all__ = ["main", "serve"] 