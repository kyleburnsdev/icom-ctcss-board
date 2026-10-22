# FreeCAD Robust MCP setup

Local setup verified on KyleBurns's Windows computer on 2026-10-22. This establishes CAD tooling for enclosure work; it does not establish enclosure dimensions or mechanical acceptance.

## Installed components

- FreeCAD **1.1.1**, existing installation: `C:\Program Files\FreeCAD 1.1\bin\freecad.exe`.
- Robust MCP server and bridge **0.6.2**, upstream release commit `eb2f6fba2a5422ad390213fae380a1acac040cdf` (tags `robust-mcp-server-v0.6.2` and `robust-mcp-workbench-v0.6.2`).
- Dedicated Python 3.12 environment: `%LOCALAPPDATA%\FreeCAD-Robust-MCP\venv`.
- Bridge workbench: `%APPDATA%\FreeCAD\v1-1\Mod\FreecadRobustMCPBridge`, copied from the release's `addon/FreecadRobustMCPBridge` directory.
- MCP Python SDK **1.30.0**, constrained to `mcp>=1.25,<2` to retain the server's SDK generation. `pip check` passed.

The server was installed from the checked-out release with pip, without editable mode. Neither installed component depends on this repository or temporary setup files. The workbench's `AutoStart` preference is enabled under `User parameter:BaseApp/Preferences/Mod/RobustMCPBridge`.

## Codex configuration and daily use

The user-level `%USERPROFILE%\.codex\config.toml` contains:

```toml
[mcp_servers.freecad]
command = 'C:\Users\KyleBurns\AppData\Local\FreeCAD-Robust-MCP\venv\Scripts\freecad-mcp.exe'
args = []
startup_timeout_sec = 60
tool_timeout_sec = 120

[mcp_servers.freecad.env]
FREECAD_MODE = "xmlrpc"
FREECAD_SOCKET_HOST = "localhost"
FREECAD_XMLRPC_PORT = "9875"
PYTHONUTF8 = "1"
```

Open FreeCAD 1.1 before using CAD tools. The bridge starts automatically. If necessary, select the **Robust MCP Bridge** workbench and use **Start MCP Bridge**. Restart Codex after adding this configuration so it can load the new server. Codex launches the stdio MCP process; a separate persistent MCP terminal is unnecessary.

The bridge listens on loopback: XML-RPC at `127.0.0.1:9875`, with socket listeners at `127.0.0.1:9876` and `[::1]:9876` observed during verification. It can execute CAD Python and access files as the current user, so keep these endpoints local and connect trusted clients.

Connection diagnostic in PowerShell:

```powershell
$env:FREECAD_MODE = 'xmlrpc'
$env:PYTHONUTF8 = '1'
& "$env:LOCALAPPDATA/FreeCAD-Robust-MCP/venv/Scripts/freecad-mcp.exe" --check
```

Explicit XML-RPC mode is required: the server otherwise defaults to embedded mode, which does not work with the external Windows Python environment.

## Verification evidence

Using an MCP SDK client over stdio, with the installed executable and XML-RPC environment:

1. MCP initialization and tool discovery succeeded: **83 tools**.
2. `list_documents` returned an empty document list before testing.
3. `create_document` created `MCPSetupSmokeTest`.
4. `create_box` created `TestBox`, a `Part::Box` measuring **20 × 15 × 5 mm**, reporting **1500 mm³** volume.
5. `save_document` wrote a nonempty native `.FCStd` file.
6. `export_step` exported one object; the output was nonempty and contained the STEP `ISO-10303-21` header.
7. `close_document` closed the test document successfully.
8. FreeCAD was closed and reopened without a startup macro. The bridge automatically restarted; `freecad-mcp --check` again reported a successful connection to **FreeCAD 1.1.1**, GUI available.
9. `codex mcp get freecad` recognized the enabled stdio configuration. Its TOML parsed successfully.

Disposable setup files remain in the ignored `.agent-scratch/freecad-mcp-setup/` directory because automatic command approval rejected scratch cleanup. They include the upstream checkout, test scripts, native/STEP test exports, package inventory, and raw test results. The installed integration does not depend on them. Native tool availability inside a newly restarted Codex session remains the final client-side check; this already-running conversation cannot reload its tool inventory.

## Sources

- [Upstream release source](https://github.com/spkane/freecad-addon-robust-mcp-server/tree/eb2f6fba2a5422ad390213fae380a1acac040cdf)
- [Official Codex MCP configuration documentation](https://developers.openai.com/codex/mcp)
