import json
import pytest

def test_ping(client):
    """Test the /ping endpoint."""
    response = client.get('/ping')
    assert response.status_code == 200
    assert 'Success' in response.get_data(as_text=True)

def test_documentation(client):
    """Test the /documentation endpoint."""
    response = client.get('/documentation')
    assert response.status_code == 200
    assert 'Zephir API Documentation' in response.get_data(as_text=True)

def test_id(client):
    """Test the /item/ endpoint."""
    response = client.get('/item/test.123testitem')
    assert response.status_code == 200
    assert 'test.123testitem' in response.get_data(as_text=True)

def test_barcode(client):
    """Test the /item/ endpoint."""
    response = client.get('/item/test.39015012078393')
    assert response.status_code == 200
    assert 'test.39015012078393' in response.get_data(as_text=True)

def test_ark(client):
    """Test the /item/ endpoint."""
    response = client.get('/item/test.ark:/13960/t1vd7kt4b')
    assert response.status_code == 200
    assert 'test.ark:/13960/t1vd7kt4b' in response.get_data(as_text=True)

def test_default_content_negotiation(client):
    response = client.get('/item/test.123testitem')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/xml'

    with pytest.raises(json.JSONDecodeError):
        response_json = json.loads(response.data)

def test_xml_content_negotiation(client):
    response = client.get('/item/test.123testitem', headers={'Accept': 'text/xml'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/xml'

    with pytest.raises(json.JSONDecodeError):
        response_json = json.loads(response.data)

def test_json_content_negotiation(client):
    response = client.get('/item/test.123testitem', headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    try:
        response_json = json.loads(response.data)
    except json.JSONDecodeError:
        pytest.fail('Response body is not valid JSON')

def test_json_overrides_xml(client):
    response = client.get('/item/test.123testitem.json', headers={'Accept': 'text/xml'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    try:
        response_json = json.loads(response.data)
    except json.JSONDecodeError:
        pytest.fail('Response body is not valid JSON')

def test_xml_overrides_json(client):
    response = client.get('/item/test.123testitem.xml', headers={'Accept': 'application/json'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/xml'

    with pytest.raises(json.JSONDecodeError):
        response_json = json.loads(response.data)