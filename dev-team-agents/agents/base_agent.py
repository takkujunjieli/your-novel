"""
Base agent class — loads role .md for system prompt + auto-wires skills.
All agents inherit from this.
"""
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from skills.registry import registry
import os


def make_gemini_agent(role_name: str) -> dict:
    """
    Build a Gemini agent config from a role name.
    Returns {"model": llm, "tools": [...], "system_prompt": "..."}
    """
    model_name = _get_model_from_role(role_name) or "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
    )
    tools = registry.get_tools(role_name)
    system_prompt = registry.load_system_prompt(role_name)
    return {"llm": llm, "tools": tools, "system_prompt": system_prompt}


def _get_model_from_role(role_name: str) -> str | None:
    """Parse the model field from role .md frontmatter."""
    import yaml
    role_path = Path(__file__).parent / "roles" / f"{role_name}.md"
    if not role_path.exists():
        return None
    content = role_path.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        meta = yaml.safe_load(parts[1])
        return meta.get("model")
    return None
