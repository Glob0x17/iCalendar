# iCloud Calendar MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Model Context Protocol (MCP) server that provides natural language calendar management for iCloud Calendar through the CalDAV protocol. This cross-platform solution enables you to interact with your iCloud Calendar using natural language commands in any MCP-compatible client.

## ✨ Features

- **🔍 List Calendars**: View all available iCloud calendars
- **📅 Event Management**: Create, read, update, and delete calendar events
- **🔄 Recurring Events**: Support for recurring event patterns
- **⏰ Smart Alarms**: Set custom reminders for events
- **🌐 Cross-Platform**: Works on macOS, Windows, and Linux
- **🔐 Secure**: Uses app-specific passwords for secure iCloud authentication
- **🤖 Natural Language**: Integrate with AI assistants for natural calendar interactions
- **🔌 MCP Compliant**: Full support for the Model Context Protocol

## 📋 Prerequisites

- Python 3.12 or higher
- An iCloud account
- An app-specific password for your Apple ID

## 🚀 Installation

### Option 1: Install from Source

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Glob0x17/iCalendar.git
   cd mcp-ical
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```


## ⚙️ Configuration

### Step 1: Generate an App-Specific Password

1. Sign in to [appleid.apple.com](https://appleid.apple.com/)
2. Navigate to "Sign-In & Security"
3. Select "App-Specific Passwords"
4. Generate a new password (e.g. named `mcp-ical`)

⚠️ An app-specific password grants access to all of iCloud over CalDAV, CardDAV and IMAP. Never commit it, and revoke it if in doubt. The username is your Apple ID address, which is not necessarily an `@icloud.com` address.

### Step 2: Provide the Credentials

Credentials are looked up in this order:

1. **Environment variables** (recommended)

   | Variable | Required | Default |
   |---|---|---|
   | `ICLOUD_USERNAME` | yes | — |
   | `ICLOUD_PASSWORD` | yes | — |
   | `CALDAV_SERVER_URL` | no | `https://caldav.icloud.com/` |

2. **`MCP_ICAL_CONFIG`**: path to a JSON file with the format of `config.json.example`
3. **`config_private.json`**, then **`config.json`** at the repository root (legacy)

**Important**: never commit `config_private.json`: it contains your credentials.

### Other Settings

| Variable | Default | Effect |
|---|---|---|
| `MCP_ICAL_LOG_LEVEL` | `INFO` | `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`. Event contents are only logged at `DEBUG` or below. Logs go to stderr. |
| `MCP_ICAL_READ_ONLY` | `false` | When `true`, `create_event`, `update_event` and `delete_event` are not registered at all. |

## 🏃 Running the Server

The server speaks MCP over stdio and is started by your MCP client. To check it manually:
```bash
ICLOUD_USERNAME=... ICLOUD_PASSWORD=... uv run mcp-ical
```
It waits on stdin with no output on stdout.

## Claude Code Configuration

`claude mcp add -e` stores values in clear text in `~/.claude.json`. To keep secrets out of it, use a wrapper that sources an env file:

```bash
mkdir -p ~/.config/mcp-ical && chmod 700 ~/.config/mcp-ical
cat > ~/.config/mcp-ical/env <<'ENV'
ICLOUD_USERNAME=your-apple-id@example.com
ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx
MCP_ICAL_LOG_LEVEL=INFO
MCP_ICAL_READ_ONLY=true
ENV
chmod 600 ~/.config/mcp-ical/env

cat > ~/.local/bin/mcp-ical-run <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
set -a; source "$HOME/.config/mcp-ical/env"; set +a
exec /ABSOLUTE/PATH/TO/uv --directory "$HOME/src/mcp-ical" run mcp-ical
WRAPPER
chmod +x ~/.local/bin/mcp-ical-run

claude mcp add --scope user icloud-calendar -- ~/.local/bin/mcp-ical-run
```

Use the absolute path of `uv` (`which uv`) to avoid `spawn uv ENOENT`. In a Claude Code session, `/mcp` shows the server status and its tools.

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "iCalendar": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/iCalendar",
        "run",
        "mcp-ical"
      ]
    }
  }
}
```

### Troubleshooting

**If you encounter "spawn uv ENOENT" error:**

![spawn uv ENOENT](https://github.com/zwrong/iCalendar/blob/main/README.assets/spawn%20uv%20ENOENT.png?raw=true)

This error occurs when the system cannot find the `uv` command in the PATH. To fix this, specify the full path to your `uv` executable:

```json
{
  "mcpServers": {
    "ical": {
      "command": "/ABSOLUTE/PATH/TO/uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/iCalendar",
        "run",
        "mcp-ical"
      ]
    }
  }
}
```

Find the path to your `uv` executable by running:
```bash
which uv
# or on Windows:
where uv
```

Replace `/ABSOLUTE/PATH/TO/uv` with the actual path returned by the command.

After Configuration of Claude Desktop, restart the  Claude Desktop and use it!

## 📚 Usage Examples

### Example 1: Check your plans

```
User: "Do I have any plans today?"

AI: I'll check your calendar for today
→ list_events("2025-11-06T00:00:00", "2025-11-06T23:59:59")
```

![iShot_2025-11-06_13.29.26](./README.assets/iShot_2025-11-06_13.29.26.png)

### Example 2: Creating an Event

```
User: "Schedule a lunch meeting with John on Friday at noon"

AI: I'll create that event for you
→ create_event({
    "title": "Lunch Meeting with John",
    "start_datetime": "2025-01-17T12:00:00",
    "end_datetime": "2025-01-17T13:00:00",
    "calendar_name": "Personal",
    "description": "Discuss project updates"
  })
```

![iShot_2025-11-05_21.35.33](./README.assets/iShot_2025-11-05_21.35.33.png)

### Example 3: Delete an Event

```
User: "Delete the lunch meeting this week"

AI: I'll create that event for you
→ create_event({
    "title": "Lunch Meeting with John",
    "start_datetime": "2025-01-17T12:00:00",
    "end_datetime": "2025-01-17T13:00:00",
    "calendar_name": "Personal",
    "description": "Discuss project updates"
  })
```

![iShot_2025-11-05_21.31.03](./README.assets/iShot_2025-11-05_21.31.03.png)

![iShot_2025-11-05_21.32.52](./README.assets/iShot_2025-11-05_21.32.52.png)

### Example 4: Setting a Reminder

```
User: "Remind me about the presentation tomorrow at 9 AM, set the reminder for 30 minutes before"

AI: I'll create the event with a 30-minute reminder
→ create_event({
    "title": "Presentation",
    "start_datetime": "2025-01-06T09:00:00",
    "end_datetime": "2025-01-06T10:00:00",
    "alarm": 30
  })
```

![iShot_2025-11-05_21.29.05](./README.assets/iShot_2025-11-05_21.29.05.png)

## 🏗️ Architecture

### Core Components

- **`server.py`**: MCP server entry point with tool definitions using MCPServer (mcp 2.x)
- **`caldav_client.py`**: CalDAVManager class for iCloud CalDAV access and CRUD operations
- **`ical.py`**: CalendarManager wrapper providing compatibility layer
- **`models.py`**: Pydantic models for request/response validation
- **`config.py`**: Configuration management with priority handling

### Dependencies

- **mcp[cli]**: Model Context Protocol framework
- **caldav** (3.x): CalDAV client library for iCloud access
- **vobject**: iCalendar file format parsing
- **loguru**: Structured logging
- **pydantic**: Data validation and serialization

## 🤝 Integration with AI Clients

This MCP server works with any MCP-compatible client, including:
- Claude Desktop
- Claude Code
- Custom MCP clients

## 🐛 Troubleshooting

### Authentication Issues

- Verify your Apple ID email is correct
- Ensure you're using an app-specific password (not your regular password)
- Check that the app-specific password hasn't expired
- Confirm 2FA is enabled on your Apple ID if required

### Connection Issues

- Verify your internet connection
- Check that iCloud Calendar is enabled in your Apple ID settings
- Ensure your firewall allows outbound HTTPS connections

### Event Creation/Update Fails

- Verify event times are in ISO format (YYYY-MM-DDTHH:MM:SS)
- Ensure start time is before end time
- Check that the calendar name exists

## 📝 Development

### Project Structure

```
mcp-ical/
├── mcp_ical/
│   ├── server.py          # MCP server entry point
│   ├── caldav_client.py   # CalDAV operations
│   ├── ical.py            # Calendar manager wrapper
│   ├── models.py          # Data models
│   └── config.py          # Configuration
├── tests/                 # Unit tests (no network)
│   └── integration/       # Need real credentials, marked `integration`
├── config.json.example       # Configuration template
├── pyproject.toml           # Project metadata
└── README.md                # This file
```

### Running the Tests

```bash
uv run pytest -m "not integration"   # unit tests, DAVClient mocked
uv run ruff check .
ICLOUD_USERNAME=... ICLOUD_PASSWORD=... uv run pytest -m integration   # read-only, against iCloud
```

## 📖 Known Issues and Solutions

### Recent Fixes (v0.1.0)

- **Fixed**: `update_event` and `delete_event` now properly handle URL-encoded event IDs
- **Fixed**: Event identification now checks both `event.id` and `event.url` attributes
- **Fixed**: Robust type checking for event data (string vs vobject)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CalDAV](https://tools.ietf.org/html/rfc4791) protocol specification
- [iCloud Calendar](https://www.icloud.com/calendar/) service
- [Model Context Protocol](https://modelcontextprotocol.io/) specification

## 📞 Support

- 📧 Email: zwrong@me.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/mcp-ical/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/mcp-ical/discussions)

---

**Made with ❤️ for the MCP community**
