import json

from fastapi.testclient import TestClient

from backend.main import app, get_engine, get_mock_engine


app.dependency_overrides[get_engine] = get_mock_engine


def test_websocket_flow():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"text": "Hello"})
        message = websocket.receive_text()
        payload = json.loads(message)

        for key in [
            "system_state",
            "interviewer_response",
            "avatar_state",
            "tts_enabled",
            "ui_mode",
            "next_action",
        ]:
            assert key in payload
        assert payload["ui_mode"] == "professional_minimal"
        assert payload["system_state"] == "TECHNICAL"
