from __future__ import annotations

from pathlib import Path
from typing import Any

from kodex.core.router import OrchestrationRouter
from kodex.adapters.local_adapter import LocalAdapter
from kodex.adapters.xarvis_adapter import XarvisAdapter
from kodex.adapters.escriba_adapter import EscribaAdapter
from kodex.adapters.github_adapter import GitHubAdapter


def get_router() -> OrchestrationRouter:
    """Configura e inyecta las dependencias del Router."""
    router = OrchestrationRouter()
    
    # Registramos los adaptadores. El orden puede definir la prioridad
    # si la lógica de can_handle es muy permisiva.
    router.register_adapter(XarvisAdapter())
    router.register_adapter(EscribaAdapter())
    router.register_adapter(GitHubAdapter())
    
    # LocalAdapter como fallback (debe ir al final si siempre devuelve True)
    router.register_adapter(LocalAdapter())
    
    return router


from kodex.repo_scanner import scan_repo
from kodex.git_ops import git_status

def orchestrate_task(task: str, path: str | Path = ".", *, use_branch: bool = True) -> dict[str, Any]:
    """
    Decide el siguiente paso más seguro para la tarea delegando
    al Router para que asigne el trabajo al Agente/Adapter adecuado.
    """
    router = get_router()
    
    # Recopilar el contexto del entorno para el Router y Adapters
    path_str = str(path)
    project_map = scan_repo(path_str)
    git_state = git_status(path_str)
    
    context = {
        "path": path_str,
        "use_branch": use_branch,
        "project_map": project_map,
        "git_state": git_state
    }
    
    return router.orchestrate(task, context)

