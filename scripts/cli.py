#!/usr/bin/env python3
"""CLI tool for YouTube AI Assistant operations."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from database.session import async_session
from services.agent_service import AgentService

app = typer.Typer(help="YouTube AI Assistant CLI")
console = Console()


@app.command()
def run(
    category: str = typer.Option("ai-tools", help="Content category"),
    resolution: str = typer.Option("1080x1920", help="Video resolution"),
    visibility: str = typer.Option("private", help="Upload visibility"),
):
    """Run the full content pipeline."""
    async def _run():
        async with async_session() as db:
            service = AgentService(db)
            console.print(Panel.fit(f"Running pipeline: {category}", style="blue"))
            results = await service.run_full_pipeline(category, resolution, visibility)
            if results.get("success"):
                console.print(f"[green]Success! Video ID: {results.get('youtube_video_id', 'N/A')}[/green]")
            else:
                console.print(f"[red]Failed: {results.get('error', 'Unknown')}[/red]")

    asyncio.run(_run())


@app.command()
def stats():
    """Show dashboard statistics."""
    async def _run():
        async with async_session() as db:
            service = AgentService(db)
            stats = await service.get_dashboard_stats()

            table = Table(title="Dashboard Stats")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            for key, value in stats.items():
                table.add_row(key.replace("_", " ").title(), str(value))

            console.print(table)

    asyncio.run(_run())


@app.command()
def ideas(
    category: str = typer.Option("ai-tools", help="Content category"),
    count: int = typer.Option(5, help="Number of ideas"),
):
    """Generate content ideas."""
    async def _run():
        async with async_session() as db:
            service = AgentService(db)
            result = await service.generate_ideas(category=category, count=count)
            console.print(f"[green]Generated {len(result)} ideas[/green]")

    asyncio.run(_run())


if __name__ == "__main__":
    app()
