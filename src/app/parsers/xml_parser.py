import requests
import xml.etree.ElementTree as ET

from app.database import DataBase, connection_for_db

# Читаем xml файл
url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
response = requests.get(url)
xml_data = response.content

# Строим корневое древо
root = ET.fromstring(xml_data)
namespace = {'ex': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}  # Пространство имен xml файла

# Создаем подключение(сессию) к базе данных
connection = connection_for_db()

db = DataBase(connection)  # Создаем объект класса для работы с базой данных

name = 'currency_rates'
db.create_table(table=name)

db.clear_table(table=name)  # Очищаем таблицу от старых данных

for cube in root.findall('.//ex:Cube[@currency]', namespace):
    currency = cube.attrib['currency']
    rate = float(cube.attrib['rate'])
    db.input_for_database(table=name, currency=currency, rate=rate)


