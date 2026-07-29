from __future__ import annotations

import httpx
from typing import Any, Dict
from kodex.adapters.base import BaseAdapter

class XarvisAdapter(BaseAdapter):
    """
    Adaptador para integrarse con XarvisCore (Puerto 5050).
    Delega las tareas de alta complejidad o análisis al Quantum Intelligence Core.
    """
    
    BASE_URL = "http://localhost:5050/api"

    @property
    def name(self) -> str:
        return "xarvis_core"

    @property
    def capabilities(self) -> list[str]:
        return ["autonomous_agent", "quantum_intelligence", "chat_mistral", "system_analysis", "complex_refactoring"]

    def can_handle(self, task: str) -> bool:
        # El Enrutador Inteligente ahora usa capabilities y LLM. Este fallback simple se mantiene.
        task_lower = task.lower()
        return "xarvis" in task_lower or "cuantico" in task_lower or "quantum" in task_lower

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la tarea al API de XarvisCore tras verificar su salud.
        """
        client = httpx.Client(timeout=10.0)
        
        # 1. Comprobar Health Check
        try:
            health_res = client.get(f"{self.BASE_URL}/health")
            health_res.raise_for_status()
        except httpx.RequestError:
            raise ConnectionError(f"No se pudo conectar a XarvisCore en {self.BASE_URL}. ¿Está encendido el xarvis_supervisor?")
        
        # 2. Delegar la tarea al chat cuántico
        print(f"[XarvisAdapter] 🔗 Conectado a XarvisCore. Delegando tarea...")
        payload = {
            "prompt": f"CONTEXTO PROYECTO: {context.get('path')}\nTAREA SOLICITADA POR KODEX: {task}",
            "model": "mistral"
        }
        
        try:
            chat_res = client.post(f"{self.BASE_URL}/quantum/chat", json=payload, timeout=60.0)
            chat_res.raise_for_status()
            data = chat_res.json()
            
            # XarvisCore devuelve un JSON con "success", "response" o "error"
            if data.get("success"):
                return {
                    "status": "success",
                    "output": {"xarvis_response": data.get("response")},
                    "artifacts": []
                }
            else:
                return {
                    "status": "xarvis_internal_error",
                    "output": {"error": data.get("error", "Error desconocido en Xarvis")},
                    "artifacts": []
                }
        except httpx.RequestError as e:
            raise RuntimeError(f"Error de red al consultar XarvisCore: {e}")
