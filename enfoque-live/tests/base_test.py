from app import setup  # Flask instance of the API
from utils import configuration
from models.database import db
from flask import url_for
import pytest

db_recreate = False


@pytest.fixture
def get_app():
    ctx_app = setup()
    # setup test db
    ctx_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_test.db'
    db.init_app(ctx_app)
    if db_recreate:
        with ctx_app.app_context():
            db.drop_all()
            db.create_all()
    yield ctx_app


@pytest.fixture
def client(get_app):
    return get_app.test_client()


@pytest.fixture
def runner(get_app):
    return get_app.test_cli_runner()


def test_root_route(client):
    # Bad login
    response = client.post('/login', data={'user': 'admin', 'password': 'adminqwe'}, follow_redirects=True)
    assert response.status_code == 401  
    
    # Test "/" route without auth
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/comprar'

    # Good login
    good_credentials = {'user': configuration.get("admin_user"), 'password': configuration.get("admin_password")}
    response = client.post('/login', data=good_credentials, follow_redirects=True)
    assert response.status_code == 200

    # Test "/" route with auth
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/panel'





"""
def test_buy_endpoint_user_limit_reached(client, monkeypatch):
    monkeypatch.setattr(configuration, 'get', lambda x: 10)
    monkeypatch.setattr(tokens_db, 'count_all_sold_tokens', lambda: 11)
    response = client.get(url_for('mp_checkout.buy'))
    assert response.status_code == 200
    assert b"Limite de usuarios alcanzado!" in response.data

    
    """
