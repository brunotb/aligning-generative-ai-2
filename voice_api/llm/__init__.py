"""
LLM module: Prompts, tools, and handlers for Gemini Live integration.

This module manages communication with the Gemini Live API:
- Prompts: System instructions and field descriptions
- Tools: Function declarations exposed to the model
- Handlers: Processing model tool calls and generating responses

The LLM module is independent of the core module and can be replaced
with different LLM integrations if needed.
"""

from .handlers import handle_tool_calls
from .prompts import build_system_prompt
from .tools import build_function_declarations, build_tool_config

__all__ = [
    # Prompts
    "build_system_prompt",
    # Tools
    "build_function_declarations",
    "build_tool_config",
    # Handlers
    "handle_tool_calls",
]
