# Project Report: Sandboxed MCP File Server

## 1. Introduction

The Sandboxed MCP File Server is a Python-based application that allows an MCP-compatible client, such as Claude Desktop, to interact with files inside a designated workspace. MCP stands for Model Context Protocol, which allows AI applications to communicate with external tools.

The project focuses on providing basic file management and Git status tools while restricting file access to a specific directory. It also includes automated security tests to check how the server handles invalid paths and potentially unsafe file operations.

The server currently runs locally through standard input/output (stdio) transport. Remote access and HTTPS deployment are outside the current implementation.

## 2. Project Objectives

The main objectives of the project are:

1. Develop an MCP server that provides file management tools.
2. Restrict file operations to a designated workspace directory.
3. Prevent unauthorized access through absolute paths, parent-directory traversal, and symbolic links.
4. Provide basic Git status and difference-checking capabilities.
5. Test the implementation using automated security tests.
6. Demonstrate communication between an MCP-compatible client and the server, including a multi-session handoff.

## 3. Project Scope

The server provides eight tools for interacting with the workspace:

- Listing files and directories
- Reading text files
- Creating and overwriting text files
- Replacing a specific occurrence of text
- Deleting files
- Searching files for text
- Checking Git repository status
- Viewing unstaged Git differences

File operations are limited to UTF-8 text files and paths within the configured workspace. The Git tools operate on the repository located in that workspace.

The project does not currently provide remote server deployment, HTTPS transport, authentication for remote users, or process-management features for a deployed service.

## 4. System Architecture

The system consists of three main parts:

**MCP-compatible client:** The client sends tool requests to the server and displays the results. Claude Desktop was configured as the client during testing.

**Python MCP server:** The server defines the available tools and processes incoming requests. It uses the MCP Python SDK and communicates through stdio.

**Workspace directory:** The `workspace/` directory stores the files that the server is allowed to manage. The server resolves requested paths against this directory and applies path-validation checks before performing file operations.

The project structure includes the server source code and security tests outside the workspace, while the workspace contains project documentation, notes, and the Git repository.

## 5. Tools and Implementation

The server implements eight MCP tools.

| Tool | Purpose |
|---|---|
| `list_files` | Lists files and directories within a requested workspace directory. |
| `read_file` | Reads a UTF-8 text file. |
| `write_file` | Creates a new text file or overwrites an existing one. |
| `str_replace` | Replaces one exact occurrence of text in a file. |
| `delete_file` | Deletes a file inside the workspace. |
| `search_files` | Searches UTF-8 files for a specified text string. |
| `git_status` | Displays the repository's short Git status and branch information. |
| `git_diff` | Displays unstaged changes to tracked files. |

The implementation uses Python's `pathlib` for path handling and file operations. Git commands are executed using Python's `subprocess.run` with an argument list, a workspace-specific working directory, captured output, and a 10-second timeout. The implementation does not use `shell=True` for these Git commands.

*Evidence note:* These implementation details come from the project's documentation drafts. They are not stated in the saved project history, and they were not confirmed against `server.py`, which was not available for review when this report was prepared and reviewed.

## 6. Security Measures

Several safeguards were implemented to reduce the risk of unauthorized file access.

### 6.1 Path validation

The `safe_path()` function validates requested paths before they are used. It rejects absolute paths, drive-specific paths, parent-directory traversal using `..`, and paths containing `.git` components.

*Evidence note:* The saved project history records that absolute paths, drive-specific paths, parent traversal, symbolic links, and direct access to Git metadata are rejected. The function name `safe_path()` and the exact `.git` component check come from the documentation drafts and were not confirmed against the source code.

### 6.2 Workspace restriction

Resolved paths are checked to ensure they remain inside the configured workspace. This helps prevent requests from accessing files outside the permitted directory.

### 6.3 Symbolic-link checks

The saved project history records that symbolic links are rejected in requested paths. Skipping symbolic links during file listing and searching is described in the project's documentation drafts but was not confirmed against the source code. These checks are intended to reduce the risk of using links to access files outside the workspace.

### 6.4 File-operation validation

The server rejects invalid operations, including attempts to use the workspace root as a file, read or delete missing files, perform a replacement when the target text does not occur exactly once, or submit an empty search query.

*Evidence note:* The saved project history records only that the automated tests cover normal and rejected file operations. The specific cases listed above come from the documentation drafts and were not confirmed against the source code or the test file.

### 6.5 Git command handling

Git commands use an argument list rather than a shell command string and have a timeout to prevent them from waiting indefinitely. The Git tools run with the workspace as their working directory. As in Section 5, these details come from the documentation drafts and were not confirmed against the source code.

These measures improve path and operation safety, but they do not establish that the server is completely secure. Additional testing and hardening would be needed before using it in a higher-risk or remotely accessible environment.

## 7. Testing and Results

The project includes an automated security test suite named `test_security.py`. The tests cover normal file operations, invalid paths, directory traversal, Git metadata restrictions, symbolic-link handling, and rejected file operations. Coverage of invalid replacement and search requests is described in the documentation drafts but is not itemized in the saved project records.

The latest recorded test result is **29 tests passed**. This is based on the project's existing test records; the tests were not rerun while this report was being prepared or reviewed. The date of that run, its raw output, and the individual test names are not recorded, and `test_security.py` was not available for review.

### 7.1 MCP client testing

Basic MCP client testing was also performed through Claude Desktop. The project history documents a temporary-file test (`mcp_tool_test_temp.txt`) that verified `write_file`, `read_file`, `str_replace`, and `delete_file`, and records that the temporary file was removed afterward. The intended sequence also included listing files, reading the file again after the replacement, and confirming that the file was no longer present. Those steps are not separately documented in the saved records and cannot be independently verified from them, and the file content, arguments, and tool outputs were not preserved. The testing records also document basic use of the file-management and Git tools.

The available records support basic functionality testing, not exhaustive testing of every tool, input combination, or security edge case.

### 7.2 Multi-session handoff

A separate client session was used to demonstrate that work could continue from saved project records. The second session read the handoff information and project documentation and checked Git status and differences. It was also assigned to write a short continuation summary, but that summary was not saved in the project files, so its content cannot be verified from the saved records.

This demonstrated that saved project notes could help a new session understand the existing implementation and continue work without relying entirely on the previous conversation.

## 8. Limitations

The project has several known limitations:

1. **Local operation only:** The server currently uses stdio transport and has not been configured for remote deployment or HTTPS.
2. **Limited Git difference reporting:** `git_diff` shows unstaged changes to tracked files. It does not display staged changes or untracked files; `git_status` provides complementary repository information.
3. **Incomplete security validation:** Although the automated test suite has a recorded result of 29 passing tests, further edge-case testing is still needed.
4. **No claim of complete security:** Path checks and other safeguards reduce certain risks but do not guarantee protection against every attack or race condition.
5. **Limited file support:** The read, write, replacement, and search tools are designed primarily for UTF-8 text files rather than arbitrary binary files.
6. **Deployment hardening remains:** Authentication, remote access controls, HTTPS configuration, and service process management have not been implemented.

## 9. Conclusion

The Sandboxed MCP File Server demonstrates how a Python application can expose file-management and Git tools through the Model Context Protocol. It includes workspace-based path restrictions, input validation, basic symbolic-link checks, and automated security tests.

The recorded testing indicates that the core file operations and security checks have been exercised, while the client handoff demonstrates how project context can be preserved between sessions. However, additional testing is needed, and the current implementation remains a local development tool rather than a remotely deployed service.

The project provides a foundation for further work on MCP tool development, filesystem safety, automated testing, and integration with AI-compatible clients.
