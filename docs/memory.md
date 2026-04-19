# Memory Management

`tiny-agent-py` uses a sliding-window memory approach backed by a per-session SQLite database. This ensures the LLM's context window stays within limits while persisting the full conversation history.

## Sliding-Window Context
The agent only retains the most recent `N` messages in the working memory (the messages actually sent to the LLM).
This is controlled by the `max_context_window` parameter during agent initialization.

## SQLite Spillover
When the number of messages exceeds `max_context_window`, the oldest messages are offloaded (spilled over) into a local SQLite database (`.tiny_agent_memory.db` by default). This guarantees that:
1. You never exceed LLM token limits.
2. The complete conversation history is preserved across agent restarts.

## Cross-Session Search
The agent has built-in capabilities to search past sessions, allowing it to retrieve information that was spilled over or discussed in entirely different sessions.
