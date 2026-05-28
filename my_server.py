from collections import defaultdict
import os
import dotenv
dotenv.load_dotenv()
from prefab_ui.app import PrefabApp
from prefab_ui.components import Badge, Card, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Row, Text
from prefab_ui.components.charts import BarChart, ChartSeries, LineChart
from fastmcp import FastMCP
from fastmcp.apps.generative import GenerativeUI
from functions.get_sleep_data import get_sleep_data as get_sleep_data_function
from functions.get_sleep_data import get_sleep_events_for_night as get_sleep_events_for_night_function
from functions.get_activity_data import get_activity_data as get_activity_data_function
from functions.get_activity_data import get_activity_data_full as get_activity_data_full_function
from functions.get_activity_data import get_activity_by_id as get_activity_by_id_function
from functions.get_activity_data import load_activity_json as load_activity_json_function


MCP_PORT = os.getenv("MCP_PORT")
MCP_HOST = os.getenv("MCP_HOST")
TRANSPORT = os.getenv("TRANSPORT")

mcp = FastMCP("GarminDbMcp",
    instructions="This is a Garmin DB server that can be used to get information about a users data.",
    )
@mcp.tool()
def get_sleep_data(start_date: str, end_date: str) -> dict:
    """Get Sleep Data for a given date or range"""
    return {"nights": get_sleep_data_function(start_date, end_date)}

def _sleep_rows_for_table(rows: list[dict]) -> list[dict]:
    """Shorter strings for table cells."""
    out: list[dict] = []

    for r in rows:
        day = r.get("day") or ""
        if isinstance(day, str) and " " in day:
            day = day.split()[0]
        out.append(
            {
                "day": day,
                "total_sleep": r.get("total_sleep") or "—",
                "deep_sleep": r.get("deep_sleep") or "—",
                "light_sleep": r.get("light_sleep") or "—",
                "rem_sleep": r.get("rem_sleep") or "—",
                "awake": r.get("awake") or "—",
                "score": r.get("score") if r.get("score") is not None else "—",
                "qualifier": r.get("qualifier") or "—",
            }
        )
    return out


@mcp.tool(app=True)
def get_sleep_data_visual(start_date: str, end_date: str) -> PrefabApp:
    """Show sleep nights in a sortable table for the given date range (SQLite)."""
    raw = get_sleep_data_function(start_date, end_date)
    table_rows = _sleep_rows_for_table(raw)
    if len(table_rows) == 0:
        return PrefabApp(view=Text("No sleep data found for the given date range."))
    with Column(gap=4, css_class="p-6") as view:
        Heading("Sleep")
        with Row(gap=2):
            Text(f"Range: {start_date} → {end_date}", css_class="text-muted-foreground")
        DataTable(
            columns=[
                DataTableColumn(key="day", header="Night", sortable=True),
                DataTableColumn(key="total_sleep", header="Total", sortable=True),
                DataTableColumn(key="deep_sleep", header="Deep"),
                DataTableColumn(key="light_sleep", header="Light"),
                DataTableColumn(key="rem_sleep", header="REM"),
                DataTableColumn(key="awake", header="Awake"),
                DataTableColumn(key="score", header="Score", sortable=True),
                DataTableColumn(key="qualifier", header="Qualifier", sortable=True),
            ],
            rows=table_rows,
            search=True,
            paginated=True,
            page_size=10,
        )

    return PrefabApp(view=view)

@mcp.tool()
def get_sleep_data_events(day: str) -> dict:
    """Get Sleep Events for a given day"""
    return {"events": get_sleep_events_for_night_function(day)}


@mcp.tool()
def get_activity_data(
    start_date: str,
    end_date: str,
    sport: str | None = None,
    sub_sport: str | None = None,
    name_contains: str | None = None,
) -> dict:
    """List activities in a date range. Optional filters: sport, sub_sport, name_contains."""
    return {
        "activities": get_activity_data_function(
            start_date,
            end_date,
            sport=sport,
            sub_sport=sub_sport,
            name_contains=name_contains,
        )
    }


@mcp.tool()
def get_activity_data_full(activity_id: str) -> dict:
    """Get Activity Data for a given activity id"""
    return {"activity_data": get_activity_data_full_function(activity_id)}

@mcp.tool()
def get_activity_data_by_id(activity_id: str) -> dict:
    """Get Activity Data for a given activity id"""
    return {"activity_data": get_activity_by_id_function(activity_id)}

@mcp.tool()
def load_activity_json(activity_id: str) -> dict:
    """Load Activity JSON for a given activity id"""
    return {"activity_json": load_activity_json_function(activity_id)}


if __name__ == "__main__":
    ##mcp.run()
    mcp.run(transport=TRANSPORT, host=MCP_HOST, port=MCP_PORT)