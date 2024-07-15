import requests


def test_create_token():
    url = 'http://127.0.0.1/tokens/action'
    data = {
        'alias': 'test_alias',
        'select_action': 'create'
    }
    response = requests.post(url, data=data)
    
    #assert response.status_code == 302  # Verificar que se recibe un código de redirección
    #assert 'test_alias' in response.headers['Location']  # Verificar que la redirección contiene el alias creado

while True:
	test_create_token()