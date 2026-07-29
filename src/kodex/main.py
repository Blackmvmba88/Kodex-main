from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON

from kodex.git_ops import git_status
from kodex.repo_scanner import scan_repo
from kodex.orchestrator import orchestrate_task
from kodex.memory import save_project, load_projects

app = typer.Typer(help="Kodex — BlackMamba Orchestration Agent")
console = Console()


@app.command()
def scan(path: str = typer.Argument(".", help="Repository path to scan"), save: bool = True) -> None:
    """Scan a repository and optionally save it to memory."""
    project = scan_repo(path)
    console.print(JSON.from_data(project))

    if save:
        save_project(project)
        console.print(f"[green]Saved project memory:[/green] {project['name']}")


@app.command()
def status(path: str = typer.Argument(".", help="Repository path")) -> None:
    """Show safe git status summary."""
    console.print(JSON.from_data(git_status(path)))


@app.command()
def doctor(path: str = typer.Argument(".", help="Repository path")) -> None:
    """Scan repo and combine project map with git state."""
    project = scan_repo(path)
    state = git_status(path)
    console.print(JSON.from_data({"project": project, "git": state}))


@app.command()
def run(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    use_branch: bool = typer.Option(True, "--branch/--no-branch", help="Use git branches if running local fallback"),
) -> None:
    """
    Convierte una intención en lenguaje natural en ejecución delegada.
    Kodex decidirá qué agente/herramienta usar (XarvisCore, Escriba, GitHub, o Local).
    """
    console.print(f"[bold blue]KODEX[/bold blue] Procesando intención: '{description}'")
    
    result = orchestrate_task(description, Path(path), use_branch=use_branch)
    
    console.print("\n[bold green]Resultado de Orquestación:[/bold green]")
    console.print(JSON.from_data(result))


if __name__ == "__main__":
    app()
