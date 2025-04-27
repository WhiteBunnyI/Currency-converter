import pytest
from app import app as flask_app
import sqlite3
import os
from unittest.mock import patch

@pytest.fixture
def app():
    # Используем временную базу данных в памяти
    flask_app.config['DATABASE'] = ':memory:'
    flask_app.config['TESTING'] = True
    yield flask_app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            flask_app.init_db()
        yield client

@pytest.fixture
def init_rates(app):
    # Фикстура для заполнения тестовых данных
    with app.app_context():
        db = sqlite3.connect(flask_app.config['DATABASE'])
        cursor = db.cursor()
        cursor.executemany(
            'INSERT INTO currency_rates VALUES (?, ?)',
            [('USD', 1.2), ('EUR', 1.0), ('GBP', 0.9)]
        )
        db.commit()
        db.close()

def test_init_db(client):
    with client.application.app_context():
        db = sqlite3.connect(flask_app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rates'")
        assert cursor.fetchone() is not None

@patch('requests.get')
def test_import_rates(mock_get, client):
    # Мокаем XML-ответ
    mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <gesmes:Envelope>
        <Cube>
            <Cube time="2023-01-01">
                <Cube currency="USD" rate="1.2"/>
                <Cube currency="GBP" rate="0.9"/>
            </Cube>
        </Cube>
    </gesmes:Envelope>"""
    mock_get.return_value.content = mock_xml.encode()

    runner = client.application.test_cli_runner()
    result = runner.invoke(args=['import'])
    assert 'Imported 3 currencies' in result.output

    # Проверяем наличие данных в БД
    with client.application.app_context():
        db = sqlite3.connect(flask_app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM currency_rates')
        assert cursor.fetchone()[0] == 3

def test_get_rates(client, init_rates):
    response = client.get('/rates')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 3
    assert any(curr['currency'] == 'USD' for curr in data)

def test_delete_rate(client, init_rates):
    response = client.delete('/rates/USD')
    assert response.status_code == 200
    # Проверяем что удалилось
    response = client.get('/rates')
    assert len(response.json) == 2

def test_update_rate(client, init_rates):
    response = client.put(
        '/rates/USD',
        json={'rate': 1.3}
    )
    assert response.status_code == 200
    # Проверяем обновление
    response = client.get('/rates')
    usd_rate = next(curr for curr in response.json if curr['currency'] == 'USD')
    assert usd_rate['rate'] == 1.3

def test_convert_currency(client, init_rates):
    test_cases = [
        {'from': 'USD', 'to': 'GBP', 'amount': 100, 'expected': 75.0},
        {'from': 'GBP', 'to': 'USD', 'amount': 100, 'expected': 133.3333},
        {'from': 'EUR', 'to': 'USD', 'amount': 100, 'expected': 120.0},
    ]
    
    for case in test_cases:
        response = client.post(
            '/convert',
            json={
                'from': case['from'],
                'to': case['to'],
                'amount': case['amount']
            }
        )
        assert response.status_code == 200
        assert round(response.json['result'], 4) == case['expected']

def test_convert_invalid_currency(client, init_rates):
    response = client.post(
        '/convert',
        json={'from': 'XXX', 'to': 'USD', 'amount': 100}
    )
    assert response.status_code == 500
    assert 'error' in response.json

def test_convert_missing_eur(client):
    # Специально создаем БД без EUR
    with client.application.app_context():
        db = sqlite3.connect(flask_app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute('INSERT INTO currency_rates VALUES ("USD", 1.2)')
        db.commit()
    
    response = client.post(
        '/convert',
        json={'from': 'USD', 'to': 'GBP', 'amount': 100}
    )
    assert response.status_code == 500
    assert 'Base currency EUR missing' in response.json['error']