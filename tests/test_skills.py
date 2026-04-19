import os
import tempfile
import pytest
from tiny_agent.skills import SkillLoader


def test_load_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        SkillLoader.load_from_file("nonexistent_file.md")


def test_load_from_file_yaml_error():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("---\nname: [invalid yaml\n---\nInstructions")
        temp_path = f.name

    try:
        skill = SkillLoader.load_from_file(temp_path)
        assert skill.name == os.path.basename(temp_path).split(".")[0]
        assert skill.instructions == "---\nname: [invalid yaml\n---\nInstructions"
    finally:
        os.unlink(temp_path)


def test_load_agents_md_not_found():
    with tempfile.TemporaryDirectory() as temp_dir:
        content = SkillLoader.load_agents_md(temp_dir)
        assert content == ""


def test_dynamic_skill_loading():
    from tiny_agent.agent import Agent

    with tempfile.TemporaryDirectory() as temp_dir:
        skill_dir = os.path.join(temp_dir, "skills")
        os.makedirs(skill_dir)

        skill_file = os.path.join(skill_dir, "test_skill.md")
        with open(skill_file, "w") as f:
            f.write(
                "---\nname: test_skill\ndescription: A test skill\n---\nThis is a test skill."
            )

        sub_skill_dir = os.path.join(skill_dir, "sub")
        os.makedirs(sub_skill_dir)
        sub_skill_file = os.path.join(sub_skill_dir, "nested_skill.md")
        with open(sub_skill_file, "w") as f:
            f.write(
                "---\nname: Nested Skill\ndescription: A nested skill\n---\nThis is nested."
            )

        agents_md = os.path.join(skill_dir, "AGENTS.md")
        with open(agents_md, "w") as f:
            f.write("Global agent instructions")

        agent = Agent(
            session_id="test_agent",
            skills_dirs=[skill_dir],
            instruction_dirs=[skill_dir],
        )

        assert "Global agent instructions" in agent.system_prompt

        assert "test_skill" in agent.system_prompt
        assert "A test skill" in agent.system_prompt
        assert "This is a test skill." not in agent.system_prompt

        assert "Nested Skill" in agent.system_prompt
        assert "A nested skill" in agent.system_prompt
        assert "This is nested." not in agent.system_prompt

        assert "load_skill" in agent.tools

        assert agent.tools["load_skill"].func("test_skill") == "This is a test skill."

        assert agent.tools["load_skill"].func("sub:nested_skill") == "This is nested."
