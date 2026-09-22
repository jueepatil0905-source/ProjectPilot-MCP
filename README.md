# ProjectPilot-MCP

ProjectPilot-MCP is an educational Python MCP server for the Cornell Engineering
Management MCP assignment.

## Domain

**Personal Productivity / Task Tracking**

The server lets a user create tasks in memory, view the current task list, and
ask for help organizing those tasks into a plan for the day.

## Architecture

The project uses the official MCP Python SDK already installed in the existing
virtual environment. The server is defined in `src/projectpilot_mcp/__init__.py`:

- `MCPServer` provides the MCP server and standard input/output transport.
- A simple Python list stores tasks for the current server session.
- Small helper functions validate input, store tasks, and build the daily plan.
- The existing `projectpilot-mcp` console entry point calls `main()`.

There is no database, authentication, network service, or external API in this
educational first version.

## MCP Features

The server exposes exactly two tools and one prompt:

### `add_task(title, priority)`

Creates an in-memory task. Titles are trimmed, checked for length and control
characters, and rejected when they contain command-like shell syntax. Priority
must be `low`, `medium`, or `high`. The tool returns a dictionary with a safe
success or validation-error message.

### `list_tasks()`

Returns all tasks currently stored in memory. Data disappears when the server
process stops.

### `plan_my_day`

Creates a prompt containing the existing tasks and asks the user to organize
them by priority with reasonable breaks.

## Setup

This project already has a `.venv`; do not delete or recreate it.

```bash
cd /Users/zuiii/Desktop/ProjectPilot-MCP
source .venv/bin/activate
python --version
```

The project requires Python 3.14 or newer. Install the direct runtime dependency
from `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

The same dependency is declared in `pyproject.toml`. No additional package is
needed for the tests because they use Python's standard-library `unittest`.

## Run The Server

The existing entry point starts the server over MCP stdio:

```bash
.venv/bin/projectpilot-mcp
```

Normally an MCP client starts this process. It is not intended to be opened as a
web page or visited in a browser.

Example tool usage from an MCP client:

```text
add_task(title="Prepare presentation", priority="high")
list_tasks()
plan_my_day
```

## Claude Desktop

The repository includes a copy-ready configuration in
`claude_desktop_config.json`. On macOS, Claude Desktop normally reads:

```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

Copy the `mcpServers.projectpilot` entry from the repository file into that
configuration. It uses the existing absolute executable path:

```json
{
	"mcpServers": {
		"projectpilot": {
			"command": "/Users/zuiii/Desktop/ProjectPilot-MCP/.venv/bin/projectpilot-mcp",
			"args": []
		}
	}
}
```

After saving the configuration, fully quit Claude Desktop and open it again so
it starts the MCP server with the new settings.

## Security Best Practices Demonstrated

### Input sanitization

`add_task` validates runtime types, trims whitespace, rejects empty or overly
long titles, rejects control characters, and allows only three priority values.
It also rejects common command-like markers. The server never passes task text
to a shell or subprocess.

### Error disclosure protection

Unexpected storage and planning failures are logged locally with generic log
messages. MCP users receive only concise generic error responses; tracebacks,
paths, environment variables, credentials, and implementation details are not
returned.

This server does not require authentication or any external secret. No `.env`
file is needed, and no credentials are stored in the repository. If a future
feature needs configuration, use environment variables or a local `.env` file
that is excluded from version control, with placeholders only in any example
file.

## Run The Tests And Exploit Demonstrations

From the project root:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

The demo includes successful task creation, invalid priority, empty title,
listing, planning, command-like/control-character input, and controlled
internal failures. Expected results include:

```text
INPUT SANITIZATION DEMO: command-like input and control characters rejected
ERROR DISCLOSURE DEMO: internal failure returned a generic safe message
```

All tests should pass. The malicious input is rejected and never stored; the
controlled error response does not contain the fake secret, path, or traceback.

## Limitations

- Tasks are in memory only and disappear when the process stops.
- There is no authentication or multi-user access control.
- Input sanitization is intentionally simple and educational, not a complete
	policy for every future task format.
- The server is designed for a local MCP client using stdio.

## Code Citations

The application code is original for this assignment. The MCP server and
decorator usage follow the official MCP Python SDK API:

https://github.com/modelcontextprotocol/python-sdk

The source file also includes a nearby SDK reference comment at the import site.
