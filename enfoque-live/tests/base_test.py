from app import setup  # Flask instance of the API
from utils import configuration
from models.database import db
from flask import url_for
import models.tokens as tokens_db
import pytest
import redis
db_recreate = False


@pytest.fixture
def get_app():
    ctx_app = setup()
    # setup test db
    ctx_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_test.db'
    ctx_app.config['REDIS_CLIENT'] = None # redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
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
    admin_user, admin_password = "admin", "admin"
    good_credentials = {'user': admin_user, 'password': admin_password}
    response = client.post('/login', data=good_credentials, follow_redirects=True)
    assert response.status_code == 200

    # Test "/" route with auth
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/panel'

    # Invalid token
    tokens_db.create_token()
    response = client.get('/play/jskdjalskdf')
    assert response.status_code == 404
