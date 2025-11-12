from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers.simplex import router


def test_generate_graph_html_endpoint():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    payload = {
        "problem_type": "maximization",
        "C": [3, 5],
        "LI": [[1, 0], [0, 2], [3, 2]],
        "LD": [4, 12, 18],
        "O": ["<=", "<=", "<="]
    }
    resp = client.post("/simplex/generate-graph-html", json=payload)
    assert resp.status_code == 200
    body = resp.text
    assert "<img" in body
    assert "data:image/png;base64" in body