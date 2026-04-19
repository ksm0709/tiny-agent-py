import os
import yaml
from typing import Any, List


class Skill:
    def __init__(
        self, name: str, description: str, instructions: str, tools: List[Any] = None
    ):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.tools = tools or []


class SkillLoader:
    @staticmethod
    def load_from_file(file_path: str) -> Skill:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = {}
        instructions = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    instructions = parts[2].strip()
                except yaml.YAMLError:
                    pass

        name = metadata.get("name", os.path.basename(file_path).split(".")[0])
        description = metadata.get("description", "")

        return Skill(name=name, description=description, instructions=instructions)

    @staticmethod
    def load_agents_md(dir_path: str = ".") -> str:
        agents_md_path = os.path.join(dir_path, "AGENTS.md")
        if os.path.exists(agents_md_path):
            with open(agents_md_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
