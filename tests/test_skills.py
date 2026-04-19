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
