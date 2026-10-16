# Technical Decisions

## 1. Programming Language Decision: Python
**Reason:** Python allows straightforward implementation and testing of MCP tools.

## 2. File Workspace Decision: Use `workspace/` as the Allowed File Directory
**Reason:** File operations should be restricted to a designated directory instead of allowing unrestricted filesystem access.

## 3. MCP Transport Decision: Use stdio for Local Development
**Reason:** Stdio allows an MCP client or MCP Inspector to launch and communicate with the server locally without requiring a network service.

## 4. Version Control Decision: Initialize Git Inside `workspace/`
**Reason:** The Git tools operate on the workspace repository and report its status and unstaged changes.

## 5. Security Decision: Validate and Resolve Requested Paths
**Reason:** Path validation helps prevent traversal outside the workspace. Additional protections reject absolute paths, drive-specific paths, symbolic links, and direct access to Git metadata.

## 6. Git Metadata Decision: Hide `.git` From File Tools
**Reason:** Git's internal metadata should not be exposed through file listing, searching, or direct file operations.

## 7. Testing Decision: Use Automated Security Tests
**Reason:** Automated tests make it easier to verify that normal file operations work and unsafe operations are rejected consistently.

**Current result:** 29 automated tests pass.

## 8. Deployment Decision: Defer Remote Access
**Reason:** The server should complete local functionality, security validation, and client integration before remote deployment is considered. HTTPS and process management will only be configured if required by the project.