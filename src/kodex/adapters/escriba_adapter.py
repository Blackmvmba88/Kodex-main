from __future__ import annotations

from typing import Any, Dict
from kodex.adapters.base import BaseAdapter


class EscribaAdapter(BaseAdapter):
    """
    Adaptador para integrarse con ESCRIBA.
    Se ocupa de documentación y conocimiento.
    """

    @property
    def name(self) -> str:
        return "escriba"

    @property
    def capabilities(self) -> list[str]:
        return ["documentation", "knowledge_base", "readme_generation"]

    def can_handle(self, task: str) -> bool:
        task_lower = task.lower()
        return "documenta" in task_lower or "readme" in task_lower or "escribe" in task_lower

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implementar la llamada a ESCRIBA
        print(f"[EscribaAdapter] Generando documentación para: {task}")
        
        return {
            "status": "success",
            "output": {"message": "Simulación: ESCRIBA generó los documentos."},
            "artifacts": ["docs/"]
        }
