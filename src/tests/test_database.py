import sqlite3
import unittest.mock
import pytest
import os
from pytest_mock import MockerFixture
try: 
    import src.app.app as server    #Нужна для того, чтобы мой IDE выдавал подсказки
except ImportError:
        import app as server


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
    

def test_get_db(get_db: sqlite3.Connection):
    assert get_db != None

@pytest.fixture
def get_rows():
    return ['currency', 'rate']

def test_init_db(get_db : sqlite3.Connection, get_rows):
    server.init_db()
    cursor = get_db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    rows = [des[0] for des in cursor.description]
    assert rows == get_rows
    
def test_get_rates(get_db : sqlite3.Connection, get_rows):
    server.init_db()
    rows = server.get_rates()
    print(dir(rows))
    assert rows == get_rows
    
def test_import_rates(mocker: MockerFixture, get_db: sqlite3.Connection):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.content = '''<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
	<gesmes:subject>Reference rates</gesmes:subject>
	<gesmes:Sender>
		<gesmes:name>European Central Bank</gesmes:name>
	</gesmes:Sender>
	<Cube>
		<Cube time='2025-04-25'>
			<Cube currency='USD' rate='1.1357'/>
			<Cube currency='JPY' rate='162.80'/>
			<Cube currency='BGN' rate='1.9558'/>
		</Cube>
	</Cube>
</gesmes:Envelope>
    '''.encode()
    
    server.init_db()
    with pytest.raises(SystemExit):
        server.import_rates()
    assert True