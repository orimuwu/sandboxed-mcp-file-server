
from pathlib import Path
from mcp.server.mcpserver import MCPServer
import subprocess

mcp = MCPServer("sandboxed-file-server")

ROOT = (Path(__file__).parent / "workspace").resolve()
ROOT.mkdir(parents=True, exist_ok=True)




def safe_path(path: str) -> Path:
    requested = Path(path)

    if requested.is_absolute() or requested.drive or requested.root:
        raise ValueError("Absolute or drive-specific paths are not allowed.")

    if ".git" in (part.lower() for part in requested.parts):
        raise ValueError("Access to Git metadata is not allowed.")

    target = ROOT / requested

    current = ROOT
    for part in requested.parts:
        if part in (".", ""):
            continue

        if part == "..":
            raise ValueError("Path traversal is not allowed.")

        current = current / part

        if current.is_symlink():
            raise ValueError("Symbolic links are not allowed.")

    target = target.resolve()

    if not target.is_relative_to(ROOT):
        raise ValueError("Access denied: path is outside the workspace.")

    return target




@mcp.tool()
def list_files(path: str = ".") -> list[str]:
    """List files and folders inside the workspace."""
    folder = safe_path(path)

    if not folder.is_dir():
        raise ValueError("Directory not found.")

    results = []

    for item in folder.rglob("*"):
        relative = item.relative_to(ROOT)

        if ".git" in (part.lower() for part in relative.parts):
            continue

        if item.is_symlink():
            continue

        if item.resolve().is_relative_to(ROOT):
            results.append(str(relative))

    return sorted(results)



@mcp.tool()
def read_file(path: str) -> str:
    """Read a UTF-8 text file inside the workspace."""
    file = safe_path(path)

    if not file.is_file():
        raise ValueError("File not found.")

    return file.read_text(encoding="utf-8")


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create or overwrite a UTF-8 text file inside the workspace."""
    file = safe_path(path)

    if file == ROOT:
        raise ValueError("A file path is required.")

    file.parent.mkdir(parents=True, exist_ok=True)
    file = safe_path(str(file.relative_to(ROOT)))
    file.write_text(content, encoding="utf-8")

    return f"File saved: {file.relative_to(ROOT)}"


@mcp.tool()
def str_replace(path: str, old: str, new: str) -> str:
    """Replace one exact text occurrence in a workspace file."""
    file = safe_path(path)

    if not file.is_file():
        raise ValueError("File not found.")

    content = file.read_text(encoding="utf-8")
    count = content.count(old)

    if count != 1:
        raise ValueError(
            f"Expected exactly one match, but found {count}."
        )

    file.write_text(content.replace(old, new, 1), encoding="utf-8")
    return "Replacement completed."


@mcp.tool()
def delete_file(path: str) -> str:
    """Delete a file inside the workspace."""
    file = safe_path(path)

    if file == ROOT or not file.is_file():
        raise ValueError("File not found or invalid path.")

    file.unlink()
    return f"Deleted: {file.relative_to(ROOT)}"



@mcp.tool()
def search_files(query: str) -> list[str]:
    """Search for text in UTF-8 files inside the workspace."""
    if not query:
        raise ValueError("Search query cannot be empty.")

    matches = []

    for file in ROOT.rglob("*"):
        relative = file.relative_to(ROOT)

        if ".git" in (part.lower() for part in relative.parts):
            continue

        if file.is_symlink():
            continue

        if not file.is_file() or not file.resolve().is_relative_to(ROOT):
            continue

        try:
            if query in file.read_text(encoding="utf-8"):
                matches.append(str(relative))
        except (UnicodeDecodeError, OSError):
            continue

    return sorted(matches)



@mcp.tool()
def git_status() -> str:
    """Show Git status for the workspace repository."""
    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        return result.stderr.strip() or "Git status unavailable."

    return result.stdout.strip() or "Working tree clean."


@mcp.tool()
def git_diff() -> str:
    """Show unstaged Git changes in the workspace repository."""
    result = subprocess.run(
        ["git", "diff", "--"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        return result.stderr.strip() or "Git diff unavailable."

    return result.stdout or "No unstaged changes."


if __name__ == "__main__":
    mcp.run(transport="stdio")
