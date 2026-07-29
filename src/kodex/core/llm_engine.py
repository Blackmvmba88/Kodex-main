from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from openai import OpenAI
import httpx

# Configuración por defecto para Ollama local
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3"

def get_client() -> OpenAI:
    """Retorna un cliente OpenAI apuntando a Ollama local con Timeouts estrictos."""
    return OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
        # Timeout de 15 segundos máximo para evitar bloqueos
        http_client=httpx.Client(timeout=15.0)
    )

def extract_json_robust(text: str) -> Dict[str, Any]:
    """Usa expresiones regulares para extraer JSON incluso si el modelo 'habla de más'."""
    try:
        # Intenta parsear directamente
        return json.loads(text)
    except json.JSONDecodeError:
        # Si falla, busca un bloque con llaves {...}
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    raise ValueError("No se pudo extraer un JSON válido del texto.")

def decide_route(task: str, adapters_info: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, str]:
    """Pide al LLM local que evalúe la tarea con blindaje contra fallos y contexto inyectado."""
    client = get_client()
    
    # Preparar reporte de contexto (limitado para no reventar memoria del LLM)
    git_state = context.get("git_state", {})
    project_map = context.get("project_map", {})
    
    # Solo pasamos la lista de archivos raíz y los detalles de git para mantener el prompt conciso
    context_report = f"""
    --- REPORTE DE CONTEXTO ---
    Archivos Raíz (Muestra): {list(project_map.get("files", {}).keys())[:15]}
    Archivos Modificados (Git): {git_state.get("staged", []) + git_state.get("unstaged", [])}
    Archivos Sin Trackear (Git): {git_state.get("untracked", [])}
    Rama Actual: {git_state.get("branch", "unknown")}
    ---------------------------
    """

    system_prompt = (
        "Eres el Enrutador Inteligente de Kodex (Director de Orquesta). "
        "Tu trabajo es analizar la instrucción del usuario junto con el reporte del repositorio actual, "
        "y elegir la herramienta/agente adecuado.\n\n"
        f"{context_report}\n\n"
        f"Herramientas disponibles: {json.dumps(adapters_info, indent=2)}\n\n"
        "Debes responder ÚNICAMENTE con un objeto JSON válido con este esquema:\n"
        "{\n"
        '  "selected_adapter": "nombre_del_adaptador_elegido",\n'
        '  "reasoning": "Breve explicación de tu decisión considerando el estado de los archivos y git."\n'
        "}\n"
        "No añadas ningún texto antes ni después del JSON. Si ninguna herramienta es adecuada, usa 'local_fallback'."
    )

    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Tarea: {task}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result_text = response.choices[0].message.content or "{}"
        return extract_json_robust(result_text)
        
    except Exception as e:
        # Graceful degradation
        return {
            "selected_adapter": "local_fallback",
            "reasoning": f"Fallback automático. Error en LLM local: {str(e)}"
        }

