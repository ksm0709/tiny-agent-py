# Markdown Skills & AGENTS.md

`tiny-agent-py` features a markdown-based skill loading system, designed to inject project-specific instructions and reusable skills directly into the system prompt.

## AGENTS.md
If an `AGENTS.md` file exists in your project root, the agent will automatically read it and prepend its contents to the system prompt. This is ideal for defining global rules, coding standards, or context specific to your project.

## Skills Loading
You can define individual skills as markdown files (e.g., `.agents/skills/my-skill/SKILL.md`). The agent can dynamically load these skills based on the user's prompt or specific commands, giving the LLM precise instructions only when needed.
