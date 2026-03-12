"""
SkillRegistry — auto-wires tools to agents based on their role .md frontmatter.
Add a skill here once, then declare it in the role file. Done.
"""
import yaml
from pathlib import Path
from skills.file_tools import read_file, write_file, list_directory
from skills.shell_tools import run_command


# ── Master skill catalogue ────────────────────────────────────────────────────
SKILL_MAP = {
    "read_file":    read_file,
    "write_file":   write_file,
    "list_dir":     list_directory,
    "run_command":  run_command,
}


class SkillRegistry:
    """Reads an agent's role .md, parses the skills list, returns tool objects."""

    ROLES_DIR = Path(__file__).parent.parent / "agents" / "roles"

    def get_tools(self, role_name: str) -> list:
        role_path = self.ROLES_DIR / f"{role_name}.md"
        if not role_path.exists():
            raise FileNotFoundError(f"Role file not found: {role_path}")

        content = role_path.read_text()
        # Parse YAML frontmatter between --- ... ---
        if content.startswith("---"):
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
        else:
            meta = {}

        skills = meta.get("skills", [])
        tools = []
        for skill in skills:
            if skill not in SKILL_MAP:
                raise ValueError(f"Unknown skill '{skill}' in role '{role_name}'")
            tools.append(SKILL_MAP[skill])
        return tools

    def load_system_prompt(self, role_name: str) -> str:
        """Returns the body of the role .md (everything after the frontmatter)."""
        role_path = self.ROLES_DIR / f"{role_name}.md"
        content = role_path.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            return parts[2].strip()
        return content.strip()


registry = SkillRegistry()
