import pytest
import web_app

@pytest.fixture
def client():
    """A test client for the app."""
    app = web_app.create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_fail(client):
    """Start with a blank database."""

    rv = client.get('/fail-me')
    assert rv.status_code == 418
