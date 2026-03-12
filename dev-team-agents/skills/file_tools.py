"""File system tools — readable/writable by agents that declare them in their role."""
from langchain_core.tools import tool
from pathlib import Path
import os


@tool
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR reading {path}: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories if needed."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"OK: wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"ERROR writing {path}: {e}"


@tool
def list_directory(path: str) -> str:
    """List files and directories at the given path."""
    try:
        entries = sorted(os.listdir(path))
        return "\n".join(entries)
    except Exception as e:
        return f"ERROR listing {path}: {e}"
