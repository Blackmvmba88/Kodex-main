from __future__ import annotations

from typing import Any, Dict
from kodex.adapters.base import BaseAdapter


class GitHubAdapter(BaseAdapter):
    """
    Adaptador para integrarse con GitHub.
    Maneja PRs, issues, y operaciones en remoto.
    """

    @property
    def name(self) -> str:
        return "github"

    @property
    def capabilities(self) -> list[str]:
        return ["pull_request", "issue_management", "code_review"]

    def can_handle(self, task: str) -> bool:
        task_lower = task.lower()
        return "pr " in task_lower or "pull request" in task_lower or "revisa" in task_lower

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implementar la llamada a la GitHub API o CLI (gh)
        print(f"[GitHubAdapter] Interactuando con GitHub para: {task}")
        
        git_state = str(context.get("git_state", ""))
        preview = git_state[:100].replace('\n', ' ') if git_state else "Sin cambios."
        print(f"[GitHubAdapter] Estado actual de git para el PR: {preview}...")
        
        return {
            "status": "success",
            "output": {"message": "Simulación: PR creado exitosamente evaluando el estado actual."},
            "artifacts": []
        }
