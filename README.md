This is an MCP server built on GarminDB.
This is in development and will improve over time because it is for my own use.

This MCP server allows AI models to pull Garmin data saved locally via GarminDB(https://github.com/tcgoetz/GarminDB), and can create Generative UI views via FastMCP + PrefabUI.
You should read about GenerativeUI here: https://gofastmcp.com/apps/generative

## Quick setup

1. Create/activate your Python virtual environment. (venv, do your thing)
2. Install dependencies:
   ```bash
   bash install_deps.sh
   ```
3. Copy `.env.example` to `.env` and set valid local paths.
3.5. Make sure Deno is installed and in your `PATH` (the install script handles this).
4. It is absolutely vital you have completed setup of GarminDB, and have synced your db. https://github.com/tcgoetz/GarminDB

Required `.env` keys:
- `MCP_PORT`
- `MCP_HOST`
- `TRANSPORT`
- `GARMIN_DBs_PATH` - Please look at the example
- `FITFILES_PATH`

## Run

From this folder:

```bash
python my_server.py
```

## I've never used an MCP locally before, what do I do
To connect this to web-available AI tools, host it behind a reverse proxy with authentication (not covered in this README).

If you want to use this within Claude Code, Codex CLI, Cursor, or any local AI connection like Cline:
- run the server
- Add the MCP connection to your tool of choice. For Cursor, example:

```json
"garmin-db": {
  "command": "/home/USER/.GarminDb/venv/bin/fastmcp",
  "args": ["run", "/home/USER/.GarminDb/my_server.py:mcp"],
  "cwd": "/home/USER/.GarminDb",
  "env": {
    "PATH": "/home/USER/.deno/bin:/usr/local/bin:/usr/bin:/bin"
  }
}
```


## Example MCP tool calls

- `get_sleep_data(start_date, end_date)`
- `get_activity_data(start_date, end_date, sub_sport="strength_training")`
- `get_activity_data_full(activity_id)`
- `load_activity_json(activity_id)`

is this the best? No.
Was AI used in creating this? Yes, mainly for some SQL filter cases, the install script, parts of this README, and **pushing to Git**.


## Example Of GenerativeUI
<img width="658" height="671" alt="image" src="https://github.com/user-attachments/assets/cc249512-f392-487d-95ba-b40d2c5edbdc" />

<img width="675" height="667" alt="image" src="https://github.com/user-attachments/assets/37af1ab9-095f-4742-8811-55674fdbe879" />

