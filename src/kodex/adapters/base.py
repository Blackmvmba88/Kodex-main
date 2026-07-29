from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAdapter(ABC):
    """
    Contrato común para cualquier herramienta o agente que Kodex pueda orquestar.
    Cada adaptador (GitHub, XarvisCore, Escriba, Local) debe implementar este contrato.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del adaptador (ej. 'xarvis_core', 'github')."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """Lista de capacidades que este adaptador puede manejar (ej. ['code_execution', 'pr_creation'])."""
        pass

    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la tarea encomendada usando la herramienta o agente subyacente.
        
        Args:
            task: Instrucción en lenguaje natural o comando estructurado.
            context: Contexto del proyecto (paths, estado de git, variables).
            
        Returns:
            Dict con el resultado de la ejecución ('status', 'output', 'artifacts').
        """
        pass

    @abstractmethod
    def can_handle(self, task: str) -> bool:
        """Determina si este adaptador es capaz de resolver (o ayudar en) la tarea solicitada."""
        pass
