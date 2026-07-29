from __future__ import annotations

from typing import Any, Dict
from kodex.adapters.base import BaseAdapter

# Opcionalmente importamos la lógica existente para no perderla.
from kodex.executor import execute_task
from kodex.shipper import ship_task

class LocalAdapter(BaseAdapter):
    """
    Fallback local. Ejecuta operaciones limitadas (edición de archivos localmente 
    usando LLMs) si no hay agentes más potentes disponibles.
    """

    @property
    def name(self) -> str:
        return "local_fallback"

    @property
    def capabilities(self) -> list[str]:
        return ["local_file_edit", "local_git_commit"]

    def can_handle(self, task: str) -> bool:
        # Por defecto, el fallback local siempre intenta manejar la tarea si otros fallan.
        return True

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        path = context.get("path", ".")
        
        # Reutilizamos la lógica legacy temporalmente
        packet = ship_task(task, path, force=True, use_branch=True)
        
        return {
            "status": "success" if packet.get("ready") else "failed",
            "output": packet,
            "artifacts": []
        }
