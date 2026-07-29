from __future__ import annotations

import json

import httpx
import pytest

from kodex.adapters.xarvis_adapter import XarvisAdapter, XarvisConnectionError


def make_client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_reuses_client_and_omits_missing_project_path() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/health"):
            return httpx.Response(200, request=request)
        return httpx.Response(
            200,
            json={"success": True, "response": "hecho"},
            request=request,
        )

    client = make_client(httpx.MockTransport(handler))
    adapter = XarvisAdapter(client=client)

    first = adapter.execute("analiza", {})
    second = adapter.execute("corrige", {"path": None})

    assert first["status"] == "success"
    assert second["status"] == "success"
    assert len(requests) == 4
    for request in requests[1::2]:
        payload = json.loads(request.content)
        assert "CONTEXTO PROYECTO" not in payload["prompt"]
        assert "None" not in payload["prompt"]


def test_uses_configured_model_and_context_override() -> None:
    payloads: list[dict[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/health"):
            return httpx.Response(200, request=request)
        payloads.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"success": True, "response": "hecho"},
            request=request,
        )

    client = make_client(httpx.MockTransport(handler))
    adapter = XarvisAdapter(model="default-model", client=client)

    adapter.execute("uno", {"path": "/proyecto"})
    adapter.execute("dos", {"xarvis_model": "task-model"})

    assert payloads[0]["model"] == "default-model"
    assert payloads[0]["prompt"].startswith("CONTEXTO PROYECTO: /proyecto\n")
    assert payloads[1]["model"] == "task-model"


@pytest.mark.parametrize("failing_endpoint", ["health", "chat"])
def test_wraps_all_http_failures_consistently(failing_endpoint: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if failing_endpoint in request.url.path:
            raise httpx.ConnectError("sin conexión", request=request)
        return httpx.Response(200, request=request)

    client = make_client(httpx.MockTransport(handler))
    adapter = XarvisAdapter(client=client)

    with pytest.raises(XarvisConnectionError):
        adapter.execute("analiza", {})


def test_closes_only_an_internally_created_client() -> None:
    adapter = XarvisAdapter()
    adapter.close()
    assert adapter._client.is_closed

    external_client = httpx.Client()
    adapter = XarvisAdapter(client=external_client)
    adapter.close()
    assert not external_client.is_closed
    external_client.close()
