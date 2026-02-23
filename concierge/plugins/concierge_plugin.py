"""
Concierge callback plugin: logs tool calls and model responses, sanitizes model output.
Bonus: before_tool_callback / after_model_callback per assignment.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from google.genai import types

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.plugins.base_plugin import BasePlugin


logger = logging.getLogger("concierge.plugin")


class ConciergeLoggingPlugin(BasePlugin):
    """
    Plugin that logs tool invocations and model responses, and optionally
    sanitizes model output (e.g. trim whitespace). Used for the bonus
    callback implementation (before_tool_callback, after_model_callback).
    """

    def __init__(self, name: str = "concierge_logging_plugin"):
        super().__init__(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> Optional[dict]:
        """Log tool name and arguments before the tool runs."""
        logger.info(
            "[before_tool] agent=%s tool=%s args=%s",
            getattr(tool_context, "agent_name", "?"),
            tool.name,
            tool_args,
        )
        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Log model response and sanitize output (strip leading/trailing whitespace)."""
        if llm_response.content and llm_response.content.parts:
            text_parts = []
            for part in llm_response.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
            if text_parts:
                preview = " ".join(text_parts)[:200]
                if len(" ".join(text_parts)) > 200:
                    preview += "..."
                logger.info(
                    "[after_model] agent=%s response_preview=%s",
                    getattr(callback_context, "agent_name", "?"),
                    preview,
                )
            # Sanitize: strip whitespace from each text part
            new_parts = []
            for part in llm_response.content.parts:
                if hasattr(part, "text") and part.text is not None:
                    new_parts.append(types.Part(text=part.text.strip()))
                else:
                    new_parts.append(part)
            new_content = types.Content(role=llm_response.content.role, parts=new_parts)
            return llm_response.model_copy(update={"content": new_content})
        return None
