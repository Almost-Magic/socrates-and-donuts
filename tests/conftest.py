"""Shared test fixtures for ELAINE test suite."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Playwright config (for Proof browser tests)."""
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="session")
def app():
    """Create Flask app once for the entire test session."""
    from app import create_app
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="session")
def client(app):
    """Create Flask test client (session-scoped to avoid blueprint re-registration)."""
    with app.test_client() as c:
        yield c
