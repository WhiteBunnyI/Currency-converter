import sqlite3
import pytest
import os
import random
from pytest_mock import MockerFixture
try: 
    import src.app.app as server    #Нужна для того, чтобы мой IDE выдавал подсказки
except ImportError:
        import app as server


db_name = "TEST.db"
currencies = [{'currency': 'USD', 'rate': 1.1357}, {'currency': 'JPY', 'rate': 162.8}, {'currency': 'BGN', 'rate': 1.9558}, {'currency': 'EUR', 'rate': 1.0}]


@pytest.fixture
def get_rows():
    return ['currency', 'rate']


@pytest.fixture
def get_currency():
    return currencies.copy()


@pytest.fixture
def get_db():
    server.DATABASE = db_name
    server.app.config['DATABASE'] = db_name
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
def import_db(mocker: MockerFixture, init_db: sqlite3.Connection, get_currency):
    currency = ""
    for i in get_currency:
        currency += (f"<Cube currency='{i["currency"]}' rate='{i["rate"]}' />\n")
        
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


def test_import_rates(import_db: sqlite3.Connection, get_currency: list):
    cursor = import_db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    rows = [dict(row) for row in cursor.fetchall()]
    assert rows == get_currency


def test_get_rates(import_db: sqlite3.Connection, get_currency: list):
    rows = server.get_rates().json
    assert rows == get_currency

'''
@pytest.mark.parametrize("_", range(len(currencies)))
def test_delete_rate(import_db: sqlite3.Connection, get_currency: list, _):
    index = random.randint(0, len(get_currency) - 1)
    currency = get_currency[index]
    get_currency.remove(currency)
    
    server.delete_rate(currency["currency"])
    
    cursor = import_db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    rows = [dict(row) for row in cursor.fetchall()]
    
    assert rows == get_currency
    

def test_update_rate(import_db: sqlite3.Connection, get_currency: list):
    pass
'''

@pytest.mark.parametrize("index", range(len(currencies) - 1))
def test_find_conversion_path(import_db: sqlite3.Connection, get_currency: list, index: int):
    from_cur = get_currency[0]["currency"]
    to_cur = get_currency[index + 1]["currency"]
    path = server.find_conversion_path(from_cur, to_cur)
    if to_cur == "EUR":
         assert path == [from_cur, "EUR"]
    else:
        assert path == [from_cur, "EUR", to_cur]


@pytest.mark.parametrize("index", range(len(currencies) - 1))
def test_convert(import_db: sqlite3.Connection, get_currency: list, index: int):
    from_cur = get_currency[0]
    to_cur = get_currency[index + 1]
    amount = round(random.randrange(50, 100), 4)
    
    result = amount / from_cur["rate"] * to_cur["rate"]
    result = round(result, 4)
    
    server.request = server.jsonify({"from": from_cur['currency'], "to": to_cur['currency'], "amount": amount})
    server_result = server.convert().json["result"]
    
    assert server_result == result
