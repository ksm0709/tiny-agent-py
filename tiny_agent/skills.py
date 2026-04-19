import os
import yaml
from typing import Any, List


class Skill:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        instructions: str,
        tools: List[Any] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.instructions = instructions
        self.tools = tools or []


class SkillLoader:
    @staticmethod
    def load_from_file(file_path: str, skill_id: str = None) -> Skill:
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
        if not skill_id:
            skill_id = name

        return Skill(
            id=skill_id,
            name=name,
            description=description,
            instructions=instructions,
            tools=metadata.get("tools", []),
        )

    @staticmethod
    def scan_skills(dirs: List[str]) -> dict:
        skills = {}
        for d in dirs:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                for file in files:
                    if file.endswith(".md") and file != "AGENTS.md":
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, d)
                        skill_id = rel_path[:-3].replace(os.sep, ":")
                        try:
                            skill = SkillLoader.load_from_file(
                                file_path, skill_id=skill_id
                            )
                            skills[skill_id] = skill
                        except Exception as e:
                            print(f"Error loading skill {file_path}: {e}")
        return skills

    @staticmethod
    def load_agents_md(dir_path: str = ".") -> str:
        agents_md_path = os.path.join(dir_path, "AGENTS.md")
        if os.path.exists(agents_md_path):
            with open(agents_md_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
