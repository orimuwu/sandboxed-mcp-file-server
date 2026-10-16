# Sandboxed MCP File Server

A local Model Context Protocol (MCP) server that allows an AI client to manage files and inspect Git changes within a designated workspace. The server uses standard input/output (stdio) for communication and restricts file operations to the `workspace/` directory.

## Features

- File and folder listing
- UTF-8 text file reading and writing
- Exact text replacement
- File deletion
- Text search across workspace files
- Git status and unstaged diff inspection
- Path validation to restrict access to the workspace
- Security tests for path traversal, symbolic links, Git metadata, and file operations

## Requirements

- Python with a compatible MCP SDK installed
- Git installed and available on the system PATH
- Claude Desktop or another compatible MCP client

## Project Structure

```text
mcp-file-server/
├── server.py
├── test_security.py
├── .venv/
└── workspace/
    ├── .git/
    ├── .gitignore
    ├── notes/
    ├── CHECKPOINTS.md
    ├── DECISIONS.md
    ├── PLAN_LOG.md
    └── PROJECT_STATE.md
```

The exact files inside `workspace/` may change as the project develops. The `.venv/` directory contains the Python virtual environment.

## Installation and Setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install the MCP SDK

```powershell
python -m pip install mcp
```

Use the project's existing environment and dependency versions when reproducing the current working setup.

### 3. Initialize the workspace Git repository

If the workspace repository has not already been initialized:

```powershell
git -C .\workspace init
```

Do not run this command again unnecessarily if the repository already exists.

### 4. Configure Claude Desktop

Add the following server entry to the Claude Desktop configuration file, adjusting the paths if the project is stored elsewhere:

```json
{
  "mcpServers": {
    "sandboxed-file-server": {
      "command": "C:/Users/User/mcp-file-server/.venv/Scripts/python.exe",
      "args": [
        "C:/Users/User/mcp-file-server/server.py"
      ]
    }
  }
}
```

Merge the `mcpServers` entry into the existing configuration rather than replacing unrelated server entries.

Restart Claude Desktop completely after saving the configuration. Confirm that the server connects and its tools are available.

### 5. Run the server manually

With the virtual environment activated:

```powershell
python server.py
```

The server communicates through stdio. When launched by an MCP client, the client manages the server process and its communication channel.

## Available Tools

| Tool | Parameters | Purpose |
|---|---|---|
| `list_files` | `path="."` | Lists files and folders under a workspace directory. |
| `read_file` | `path` | Reads a UTF-8 text file. |
| `write_file` | `path`, `content` | Creates or overwrites a UTF-8 text file. |
| `str_replace` | `path`, `old`, `new` | Replaces text only when exactly one match exists. |
| `delete_file` | `path` | Deletes a file inside the workspace. |
| `search_files` | `query` | Searches UTF-8 files for a text string. |
| `git_status` | None | Returns the workspace repository's short Git status and branch. |
| `git_diff` | None | Returns unstaged changes to tracked files. |

### Tool Behavior

- `list_files` returns a sorted list of relative paths.
- `read_file` returns the file contents as text.
- `write_file` returns a message confirming the saved path.
- `str_replace` returns a success message or raises an error if the match count is not exactly one.
- `delete_file` returns a deletion confirmation.
- `search_files` returns a sorted list of matching file paths.
- `git_status` returns Git's short status output or a fallback message.
- `git_diff` returns the unstaged diff or a message indicating there are no unstaged changes.

## Security Measures

The server uses `safe_path()` to validate paths before performing file operations.

Implemented protections include:

- Rejecting absolute paths and drive-specific paths.
- Rejecting parent-directory traversal using `..`.
- Rejecting paths that directly reference `.git` metadata.
- Rejecting symbolic links encountered during path validation.
- Resolving paths and verifying that they remain inside the workspace.
- Hiding `.git` metadata from file listings and text search.
- Applying a 10-second timeout to Git subprocess calls.

The server does not use a shell to execute Git commands.

**Important:** These protections reduce the risk of unauthorized file access but do not prove that every possible attack has been prevented. Additional security testing is still needed.

## Running the Security Tests

From the project root, activate the virtual environment and run:

```powershell
python -m unittest -v
```

The latest recorded test run passed **29 tests**.

The test suite covers normal file operations, path traversal, absolute and drive-specific paths, symbolic links, Git metadata visibility, empty searches, and text replacement when there are zero or multiple matches.

The test count and results should be reverified when running the project in a new environment.

## Limitations

- The server is configured for local stdio communication.
- HTTPS and remote deployment are not configured.
- Separate process-management or service-hosting infrastructure has not been configured.
- `git_diff` does not show untracked files or staged changes.
- The server operates on UTF-8 text files; it is not intended as a general binary-file editor.
- The existing security tests do not cover every possible edge case.

## Project Status

The server is connected to Claude Desktop, and all eight tools have been exercised at a basic level. A multi-session demonstration also confirmed that a separate chat could recover saved project context and continue the work.

The latest recorded security test result is 29 passing tests. Further security and Git tool testing may still be needed.

## License

No license has been specified for this project.
