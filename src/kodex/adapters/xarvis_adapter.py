from __future__ import annotations

from typing import Any, Dict

import httpx

from kodex.adapters.base import BaseAdapter


class XarvisConnectionError(ConnectionError):
    """Fallo al comunicarse con la API de XarvisCore."""


class XarvisAdapter(BaseAdapter):
    """
    Adaptador para integrarse con XarvisCore (Puerto 5050).
    Delega las tareas de alta complejidad o análisis al Quantum Intelligence Core.
    """

    BASE_URL = "http://localhost:5050/api"

    def __init__(
        self,
        *,
        base_url: str = BASE_URL,
        model: str = "mistral",
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = client or httpx.Client(timeout=10.0)
        self._owns_client = client is None

    def close(self) -> None:
        """Libera las conexiones del cliente HTTP creado por el adaptador."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> XarvisAdapter:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def name(self) -> str:
        return "xarvis_core"

    @property
    def capabilities(self) -> list[str]:
        return [
            "autonomous_agent",
            "quantum_intelligence",
            "chat_mistral",
            "system_analysis",
            "complex_refactoring",
        ]

    def can_handle(self, task: str) -> bool:
        # El enrutador usa capabilities y LLM; se conserva este fallback simple.
        task_lower = task.lower()
        return (
            "xarvis" in task_lower
            or "cuantico" in task_lower
            or "quantum" in task_lower
        )

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía la tarea al API de XarvisCore tras verificar su salud.
        """
        # 1. Comprobar Health Check
        try:
            health_res = self._client.get(f"{self.base_url}/health")
            health_res.raise_for_status()
        except httpx.HTTPError as exc:
            raise XarvisConnectionError(
                f"No se pudo conectar a XarvisCore en {self.base_url}. "
                "¿Está encendido el xarvis_supervisor?"
            ) from exc

        # 2. Delegar la tarea al chat cuántico
        print("[XarvisAdapter] 🔗 Conectado a XarvisCore. Delegando tarea...")
        prompt_parts = []
        project_path = context.get("path")
        if project_path:
            prompt_parts.append(f"CONTEXTO PROYECTO: {project_path}")
        prompt_parts.append(f"TAREA SOLICITADA POR KODEX: {task}")

        payload = {
            "prompt": "\n".join(prompt_parts),
            "model": context.get("xarvis_model") or self.model,
        }

        try:
            chat_res = self._client.post(
                f"{self.base_url}/quantum/chat", json=payload, timeout=60.0
            )
            chat_res.raise_for_status()
            data = chat_res.json()

            # XarvisCore devuelve un JSON con "success", "response" o "error"
            if data.get("success"):
                return {
                    "status": "success",
                    "output": {"xarvis_response": data.get("response")},
                    "artifacts": [],
                }
            else:
                return {
                    "status": "xarvis_internal_error",
                    "output": {
                        "error": data.get("error", "Error desconocido en Xarvis")
                    },
                    "artifacts": [],
                }
        except httpx.HTTPError as exc:
            raise XarvisConnectionError(
                f"Error al consultar XarvisCore en {self.base_url}: {exc}"
            ) from exc
