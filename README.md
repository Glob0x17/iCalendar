# iCloud Calendar MCP Server

<!-- mcp-name: io.github.Glob0x17/mcp-icloud-caldav -->

[![PyPI](https://img.shields.io/pypi/v/mcp-icloud-caldav.svg)](https://pypi.org/project/mcp-icloud-caldav/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io/) server that gives MCP clients access to iCloud Calendar
over CalDAV: list calendars, read, create, update, move and delete events. It works on Linux, macOS and Windows,
since it talks to iCloud directly instead of going through the macOS Calendar app.

This is a maintained fork of [zwrong/iCalendar](https://github.com/zwrong/iCalendar), itself derived from the macOS
`mcp-ical` server. See [Changes in this fork](#changes-in-this-fork).

## Tools

| Tool | Description |
|---|---|
| `list_calendars` | Names of the available calendars |
| `list_events` | Events in a date range, optionally for one calendar, sorted by start time |
| `create_event` | New event: title, times, all-day, location, notes, URL, alarms, recurrence |
| `update_event` | Change any of those fields, or move the event to another calendar |
| `delete_event` | Delete an event by identifier |
| `debug_calendar_connection` | Connection check: calendars and event counts over the last 7 days |

The `calendars://list` resource also lists the calendars. With `MCP_ICAL_READ_ONLY=true`, the three write tools are
not registered at all.

## Requirements

- Python 3.12 or later and [uv](https://docs.astral.sh/uv/)
- An Apple ID with iCloud Calendar enabled
- An **app-specific password** for that Apple ID

### App-specific password

1. Sign in to [appleid.apple.com](https://appleid.apple.com/), open **Sign-In and Security**, then
   **App-Specific Passwords**.
2. Generate a password, for example named `mcp-icloud-caldav`.

The username is your Apple ID address, which is not necessarily an `@icloud.com` address.
An app-specific password gives access to iCloud CalDAV, CardDAV and IMAP: keep it out of version control and revoke
it if it leaks.

## Installation

The package is published on PyPI as `mcp-icloud-caldav`. With [uv](https://docs.astral.sh/uv/), MCP clients can
start it directly, without a separate install step:

```bash
uvx mcp-icloud-caldav
```

`uvx` downloads the package into a cached, isolated environment on first use. To install it permanently instead:
`uv tool install mcp-icloud-caldav` (or `pipx install mcp-icloud-caldav`).

From source:

```bash
git clone https://github.com/Glob0x17/mcp-icloud-caldav.git mcp-icloud-caldav
cd mcp-icloud-caldav
uv sync --no-dev
uv run mcp-icloud-caldav
```

## Configuration

Credentials are read in this order:

1. **Environment variables** (recommended)

   | Variable | Required | Default |
   |---|---|---|
   | `ICLOUD_USERNAME` | yes | |
   | `ICLOUD_PASSWORD` | yes | |
   | `CALDAV_SERVER_URL` | no | `https://caldav.icloud.com/` |

2. **`MCP_ICAL_CONFIG`**: path to a JSON file shaped like [`config.json.example`](config.json.example)
3. **`config_private.json`**, then **`config.json`**, at the repository root (kept for compatibility)

Other settings:

| Variable | Default | Effect |
|---|---|---|
| `MCP_ICAL_READ_ONLY` | `false` | `true` leaves out `create_event`, `update_event` and `delete_event` |
| `MCP_ICAL_LOG_LEVEL` | `INFO` | `TRACE`, `DEBUG`, `INFO`, `WARNING` or `ERROR`. Logs go to stderr |

The server speaks MCP over stdio and is started by the client. To check it by hand:

```bash
ICLOUD_USERNAME=you@example.com ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx uvx mcp-icloud-caldav
```

It waits on stdin and prints nothing on stdout.

## Client setup

Use the absolute path of `uvx` (`which uvx`) if the client cannot find it: clients often start servers without your
shell `PATH`, which shows up as `spawn uvx ENOENT`.

### Keeping the password out of the client config

Most clients store `env` values in clear text in their config file. A small wrapper that reads an env file avoids
that:

```bash
mkdir -p ~/.config/mcp-icloud-caldav && chmod 700 ~/.config/mcp-icloud-caldav
cat > ~/.config/mcp-icloud-caldav/env <<'EOF'
ICLOUD_USERNAME=you@example.com
ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx
MCP_ICAL_READ_ONLY=true
EOF
chmod 600 ~/.config/mcp-icloud-caldav/env

cat > ~/.local/bin/mcp-icloud-caldav-run <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
set -a; source "$HOME/.config/mcp-icloud-caldav/env"; set +a
exec /absolute/path/to/uvx mcp-icloud-caldav
EOF
chmod +x ~/.local/bin/mcp-icloud-caldav-run
```

Then point the client at `~/.local/bin/mcp-icloud-caldav-run`. Starting read-only and switching to `false` once reading works
is a sensible first step.

### Claude Desktop

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "icloud-calendar": {
      "command": "uvx",
      "args": ["mcp-icloud-caldav"],
      "env": {
        "ICLOUD_USERNAME": "you@example.com",
        "ICLOUD_PASSWORD": "xxxx-xxxx-xxxx-xxxx"
      }
    }
  }
}
```

or, with the wrapper, `"command": "/home/you/.local/bin/mcp-icloud-caldav-run"` and no `env`.

### Claude Code

```bash
claude mcp add --scope user icloud-calendar \
  -e ICLOUD_USERNAME=you@example.com -e ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx \
  -- uvx mcp-icloud-caldav
```

or, with the wrapper, `claude mcp add --scope user icloud-calendar -- ~/.local/bin/mcp-icloud-caldav-run`.

`/mcp` in a session shows the server state and its tools.

### Other clients

Any MCP client that can start a stdio server works: run `uvx mcp-icloud-caldav` with the environment variables above.
The server is also listed in the [MCP Registry](https://registry.modelcontextprotocol.io/) as
`io.github.Glob0x17/mcp-icloud-caldav`.

## Behavior worth knowing

- **Times.** Event times are written in UTC. A time with an offset (`2030-01-07T09:30:00+01:00`) is converted, and a
  time without one is taken as the machine's local time. Times are shown back in the machine's timezone. All-day
  events are written as dates, with the end date exclusive as the iCalendar standard requires.
- **Moving between calendars.** iCloud refuses the same event UID in two calendars, so a move cannot be
  "copy then delete". `update_event` with `calendar_name` uses a WebDAV `MOVE`, which is atomic on the server: if it
  fails, the event stays where it was. A move without other changes keeps the original iCalendar data untouched.
- **Finding events.** Listings fill an in-memory index (UID to URL) that lives as long as the server process.
  Lookups then go straight to the event, falling back to the `<calendar>/<UID>.ics` URL iCloud uses for most
  events, and only then to a scan of all calendars. iCloud does not support CalDAV UID searches.
- **Volume.** iCloud returns any number of events per request. The practical limit is the client: many cap a tool
  result at around 25,000 tokens, roughly 300 events in this server's output, so split long ranges.
- **Scope.** Only calendars hosted on iCloud are visible. Exchange, Google or other accounts added to the Calendar
  app on a device are not reachable through iCloud CalDAV, and neither are read-only subscribed (ICS) calendars.

## Privacy and security

- The only network destination is the configured CalDAV server; there is no telemetry.
- The password never appears in logs, at any level, nor in the configuration object's `repr`.
- Logs go to stderr only, since stdout carries the MCP protocol. Event contents (titles, notes) are logged only at
  `DEBUG` or below; at `INFO`, only identifiers. Some clients save server stderr to disk, so keep `DEBUG` for
  troubleshooting.
- Dependencies are locked in `uv.lock` and resolved from the official PyPI index only.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401 Unauthorized` | Regular Apple ID password instead of an app-specific one, or a revoked one |
| `spawn uv ENOENT` | `uv` is not on the client's `PATH`: use its absolute path |
| No events returned | Wrong date range, an event in a non-iCloud or subscribed calendar, or a timezone mix-up |
| Server does not respond | Something writes to stdout and breaks the stdio protocol |
| `Calendar 'X' not found` | Calendar names are case-sensitive: check `list_calendars` |

`debug_calendar_connection` and `MCP_ICAL_LOG_LEVEL=DEBUG` help narrow things down.

## Development

```bash
uv sync
uv run pytest -m "not integration"   # unit tests, CalDAV client mocked, no network
uv run ruff check .
```

Integration tests run against a real account, read-only, and are skipped unless credentials are set:

```bash
ICLOUD_USERNAME=... ICLOUD_PASSWORD=... uv run pytest -m integration
```

Project layout:

```
mcp_icloud_caldav/
├── server.py          # MCP server, tool registration, logging setup
├── caldav_client.py   # CalDAV access: search, create, update, move, delete, event index
├── ical.py            # Thin calendar manager used by the server
├── models.py          # Event and request models, iCalendar parsing
└── config.py          # Configuration loading
tests/                 # Unit tests
tests/integration/     # Read-only tests against a real account
```

## Changes in this fork

Compared with zwrong/iCalendar 0.1.0:

- **Dependencies.** Lockfile regenerated from the official PyPI index (it resolved packages through a third-party
  mirror over plain HTTP). Upgrade to `mcp` 2.x (`FastMCP` became `MCPServer`) and `caldav` 3.x; the original code no
  longer starts against current releases.
- **Configuration.** Environment variables, `MCP_ICAL_CONFIG`, read-only mode, configurable log level, no event
  contents in logs above `DEBUG`.
- **Fixes.**
  - Creating an event with a timezone offset failed (`Unable to guess TZID`); all-day events and recurrence end
    dates were written incorrectly.
  - Alarms were never read back.
  - Updating an event without a location, notes or URL failed; changing its time produced invalid iCalendar data.
  - Moving an event deleted it before saving the copy, so a failed save lost it.
  - New events got a UID containing spaces and the machine's hostname.
- **Behavior.** Events sorted by start time, compact output without empty fields, in-memory event index.
- **Tests.** Unit tests for configuration, read-only mode, logging, iCalendar output, moves and lookups.
- **Packaging.** Published on PyPI as `mcp-icloud-caldav` and listed in the MCP Registry. The Python package and the
  command are renamed from `mcp_ical` / `mcp-ical`, which clashed with the original macOS project. The unused
  `mcp[cli]` extra was dropped.

## Credits and license

MIT, see [LICENSE](LICENSE).

- The original macOS `mcp-ical` server (Omar D.), whose copyright notice is kept in `LICENSE`
- [zwrong/iCalendar](https://github.com/zwrong/iCalendar), the iCloud CalDAV port this fork builds on
- [python-caldav](https://github.com/python-caldav/caldav) and the
  [Model Context Protocol](https://modelcontextprotocol.io/) Python SDK
