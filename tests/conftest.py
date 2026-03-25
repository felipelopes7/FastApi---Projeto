import pytest
from fastapi.testclient import TestClient

from fastaulas.app import app


@pytest.fixture
def client():
    return TestClient(app)
