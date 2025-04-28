import sqlite3
import pytest
import os
from pytest_mock import MockerFixture
try: 
    import src.app.app as server    #Нужна для того, чтобы мой IDE выдавал подсказки
except ImportError:
        import app as server


@pytest.fixture
def get_rows():
    return ['currency', 'rate']


@pytest.fixture
def get_db():
    server.DATABASE = "TEST.db"
    server.app.config['DATABASE'] = ':memory:'
    server.app.config['TESTING'] = True
    with server.app.app_context():
        db = server.get_db()    
        yield db
        db.execute('DELETE FROM currency_rates')
        db.commit()
        db.close()
    

@pytest.fixture
def init_db(get_db: sqlite3.Connection):
    server.init_db()
    return get_db


@pytest.fixture
def get_currency():
    return [{'currency': 'USD', 'rate': 1.1357}, {'currency': 'JPY', 'rate': 162.8}, {'currency': 'BGN', 'rate': 1.9558}, {'currency': 'EUR', 'rate': 1.0}]


@pytest.fixture
def import_db(mocker: MockerFixture, init_db: sqlite3.Connection, get_currency):
    currency = ""
    for i in get_currency:
        currency.join(f"<Cube currency='{i["currency"]}' rate='{i["rate"]}' />\n")
        
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.content = f'''<?xml version="1.0" encoding="UTF-8"?>
    <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
        <gesmes:subject>Reference rates</gesmes:subject>
        <gesmes:Sender>
            <gesmes:name>European Central Bank</gesmes:name>
        </gesmes:Sender>
        <Cube>
            <Cube time='2025-04-25'>
                {currency}
            </Cube>
        </Cube>
    </gesmes:Envelope>
        '''.encode()
    with pytest.raises(SystemExit):
        server.import_rates()
    return init_db


def test_get_db(get_db: sqlite3.Connection):
    assert get_db != None


def test_init_db(init_db: sqlite3.Connection, get_rows):
    cursor = init_db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    rows = [des[0] for des in cursor.description]
    assert rows == get_rows


def test_import_rates(import_db: sqlite3.Connection, get_currency):
    cursor = import_db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    rows = [dict(row) for row in cursor.fetchall()]
    assert rows == get_currency


def test_get_rates(import_db: sqlite3.Connection, get_currency):
    rows = server.get_rates()
    assert rows.get_json() == get_currency
