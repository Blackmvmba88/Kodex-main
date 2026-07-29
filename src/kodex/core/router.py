from __future__ import annotations

from typing import Any, Dict, List

from rich.console import Console
from rich.prompt import Confirm

from kodex.adapters.base import BaseAdapter
from kodex.core.llm_engine import decide_route

console = Console()

class OrchestrationRouter:
    """
    Director de orquesta. Recibe una intención en lenguaje natural, analiza 
    los adaptadores disponibles y decide qué agente/herramienta debe ejecutar la tarea.
    """

    def __init__(self):
        self.adapters: List[BaseAdapter] = []

    def register_adapter(self, adapter: BaseAdapter) -> None:
        """Registra un nuevo adaptador."""
        self.adapters.append(adapter)

    def route_task(self, task: str, context: Dict[str, Any]) -> BaseAdapter | None:
        """Enruta la tarea consultando al modelo local de Ollama."""
        adapters_info = [
            {"name": a.name, "capabilities": a.capabilities} 
            for a in self.adapters
        ]
        
        console.print("[dim]Pensando (consultando Ollama local con contexto)...[/dim]")
        decision = decide_route(task, adapters_info, context)
        
        selected_name = decision.get("selected_adapter", "local_fallback")
        reasoning = decision.get("reasoning", "Sin razonamiento provisto.")
        
        console.print(f"\n[bold yellow]Decisión del Router:[/bold yellow] {selected_name}")
        console.print(f"[italic dim]Razonamiento: {reasoning}[/italic dim]\n")
        
        for adapter in self.adapters:
            if adapter.name == selected_name:
                return adapter
                
        # Si el modelo alucina un nombre, vamos al fallback
        for adapter in self.adapters:
            if adapter.name == "local_fallback":
                return adapter
        return None

    def orchestrate(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta la ejecución completa de la tarea."""
        adapter = self.route_task(task, context)
        
        if not adapter:
            return {
                "status": "error",
                "message": "Ningún agente o herramienta disponible puede manejar esta tarea.",
                "task": task
            }
            
        if not Confirm.ask(f"¿Deseas delegar esta tarea a [bold cyan]{adapter.name}[/bold cyan]?"):
            console.print("[red]Operación cancelada por el usuario.[/red]")
            return {"status": "cancelled"}
            
        console.print(f"[*] Delegando tarea a: {adapter.name}...")
        
        # [Defensa contra crasheos de agentes externos]
        try:
            result = adapter.execute(task, context)
            return result
        except Exception as e:
            console.print(f"[bold red]Fallo Crítico en el Adaptador {adapter.name}:[/bold red] {e}")
            return {
                "status": "adapter_failed",
                "message": f"El agente {adapter.name} falló durante la ejecución.",
                "error": str(e),
                "task": task
            }

