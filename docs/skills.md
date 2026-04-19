# Markdown Skills & AGENTS.md

`tiny-agent-py` features a markdown-based skill loading system, designed to inject project-specific instructions and reusable skills directly into the system prompt.

## AGENTS.md
If an `AGENTS.md` file exists in your project root, the agent will automatically read it and prepend its contents to the system prompt. This is ideal for defining global rules, coding standards, or context specific to your project.

## Skills Loading (Lazy Load)
You can define individual skills as markdown files (e.g., `.agents/skills/my-skill/SKILL.md`). The agent scans these directories and extracts the metadata (name and description) to provide a catalog of available skills in the system prompt.

To save token usage and prevent context overflow, the actual instructions of the skills are **not** loaded entirely upfront. Instead, the agent provides a `load_skill` tool. When the LLM decides it needs a specific skill based on its description, it can call `load_skill(skill_id)` to lazy-load the full instructions into the context.

### Nested Skills
The skill loader supports nested directories. A skill located at `sub/nested_skill.md` will be assigned a specific ID like `sub:nested_skill`, allowing you to organize skills logically.
