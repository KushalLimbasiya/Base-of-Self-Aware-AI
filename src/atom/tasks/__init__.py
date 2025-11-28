"""Task execution - web search, automation, commands."""

from atom.tasks.task_executor import InputExecution, NonInputExecution
from atom.tasks.web_search import WebSearch

__all__ = [
    "InputExecution",
    "NonInputExecution",
    "WebSearch",
]
