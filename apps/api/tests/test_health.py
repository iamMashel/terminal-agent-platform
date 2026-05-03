import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_health_endpoint() -> None:
    async def request_health() -> dict[str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        return response.json()

    assert anyio.run(request_health) == {
        "status": "ok",
        "service": "terminal-agent-api",
    }
