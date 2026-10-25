"""Defense in depth: block any real socket connection for the entire test session, so
that even a bug in a test's own mocking could not silently reach the network."""
import socket

import pytest


@pytest.fixture(autouse=True)
def _block_all_sockets(monkeypatch):
    def _guard(*args, **kwargs):
        raise AssertionError("a test attempted to open a real network socket; this test suite must be fully offline")

    monkeypatch.setattr(socket.socket, "connect", _guard)
    yield
