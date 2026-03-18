"""Shell tools — used by the executor layer to call Claude Code CLI."""
from langchain_core.tools import tool
import subprocess
import os


CLAUDE_CLI = os.getenv("CLAUDE_CLI_PATH", "/Users/takku/.local/bin/claude")
PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/Users/takku/Documents/ML-EKS-copy")


@tool
def run_command(command: str, cwd: str = PROJECT_ROOT) -> str:
    """Run a shell command and return its stdout + stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout or ""
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 120s"
    except Exception as e:
        return f"ERROR: {e}"


def run_claude_code(prompt: str, cwd: str = PROJECT_ROOT) -> str:
    """
    Call Claude Code CLI in non-interactive (print) mode.
    Used by executor agents (Engineer, UI Designer, Tester).
    """
    try:
        result = subprocess.run(
            [CLAUDE_CLI, "--print", "--dangerously-skip-permissions", prompt],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max for coding tasks
        )
        output = result.stdout or ""
        if result.returncode != 0 and result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output or "(no output from Claude Code)"
    except FileNotFoundError:
        return f"ERROR: claude CLI not found at {CLAUDE_CLI}. Check CLAUDE_CLI_PATH in .env"
    except subprocess.TimeoutExpired:
        return "ERROR: Claude Code timed out after 5 minutes"
    except Exception as e:
        return f"ERROR calling Claude Code CLI: {e}"
