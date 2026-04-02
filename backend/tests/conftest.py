import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
from typing import Generator


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_whatsapp_text() -> str:
    return """
[27/12/2023, 10:45:00] Alice: Hey Bob! How are you doing today?
[27/12/2023, 10:46:30] Bob: Hey Alice. I'm doing okay, just a bit busy.
[27/12/2023, 10:47:00] Alice: Oh, I see. Anything I can help with?
[27/12/2023, 10:48:15] Bob: Not really, thanks for asking though.
[27/12/2023, 10:49:00] Alice: K.
"""

@pytest.fixture
def sample_android_text() -> str:
    return """
27/12/2023, 10:45 - Alice: Hey Android user.
27/12/2023, 10:46 - Bob: Hi there.
27/12/2023, 10:47 - Alice: <Media omitted>
27/12/2023, 10:48 - Messages are encrypted
"""
