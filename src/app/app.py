import requests
import xml.etree.ElementTree as ET
import sqlite3
from flask import Flask, jsonify, request, g, render_template
from flask_cors import CORS
from collections import deque

app = Flask(__name__)
CORS(app)
DATABASE = 'currency.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS currency_rates (
                currency TEXT PRIMARY KEY,
                rate REAL NOT NULL
            )
        ''')
        db.commit()


@app.cli.command('import')
def import_rates():
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    namespaces = {'ex': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
    rates = {}
    
    for cube in root.findall('.//ex:Cube[@currency]', namespaces):
        currency = cube.attrib['currency']
        rate = float(cube.attrib['rate'])
        rates[currency] = rate

    rates['EUR'] = 1.0
    print(rates)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM currency_rates')
    for currency, rate in rates.items():
        cursor.execute('INSERT INTO currency_rates VALUES (?, ?)', (currency, rate))
    db.commit()
    print(f"Imported {len(rates)} currencies")


@app.route('/rates', methods=['GET'])
def get_rates():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM currency_rates')
    return jsonify([dict(row) for row in cursor.fetchall()])


@app.route('/rates/<currency>', methods=['DELETE'])
def delete_rate(currency):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM currency_rates WHERE currency = ?', (currency,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200


@app.route('/rates/<currency>', methods=['PUT'])
def update_rate(currency):
    db = get_db()
    cursor = db.cursor()
    new_rate = request.json.get('rate')
    cursor.execute('UPDATE currency_rates SET rate = ? WHERE currency = ?', (new_rate, currency))
    db.commit()
    return jsonify({'message': 'Updated'}), 200


def find_conversion_path(from_curr, to_curr):
    db = get_db()
    cursor = db.cursor()

    # Проверяем существование обеих валют в БД
    cursor.execute('SELECT currency FROM currency_rates WHERE currency IN (?, ?)', (from_curr, to_curr))
    existing = [row['currency'] for row in cursor.fetchall()]

    if from_curr not in existing:
        raise ValueError(f"Currency {from_curr} not found")
    if to_curr not in existing:
        raise ValueError(f"Currency {to_curr} not found")

    # Получаем все доступные валюты
    cursor.execute('SELECT currency FROM currency_rates')
    currencies = [row['currency'] for row in cursor.fetchall()]

    # Строим граф конверсии
    graph = {curr: ['EUR'] for curr in currencies if curr != 'EUR'}
    graph['EUR'] = currencies

    # Поиск в ширину
    queue = deque([[from_curr]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == to_curr:
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path.copy()
                new_path.append(neighbor)
                queue.append(new_path)

    return None


@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        from_curr = data['from'].upper()
        to_curr = data['to'].upper()
        amount = float(data['amount'])

        # Проверка наличия базовой валюты EUR
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT rate FROM currency_rates WHERE currency = "EUR"')
        if not cursor.fetchone():
            return jsonify({'error': 'Base currency EUR missing'}), 500

        # Логика конвертации
        path = find_conversion_path(from_curr, to_curr)
        total = amount

        for i in range(len(path)-1):
            current = path[i]
            next_curr = path[i+1]

            # Всегда получаем курс next_curr относительно EUR
            cursor.execute('SELECT rate FROM currency_rates WHERE currency = ?', (next_curr,))
            row = cursor.fetchone()
            rate = row['rate']

            if current == 'EUR':
                total *= rate  # EUR → next_curr
            else:
                # Конвертация current → EUR
                cursor.execute('SELECT rate FROM currency_rates WHERE currency = ?', (current,))
                current_rate = cursor.fetchone()['rate']
                total /= current_rate  # current → EUR
                total *= rate          # EUR → next_curr

        return jsonify({'result': round(total, 4)})

    except Exception as e:
        app.logger.error(f"Ошибка: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal error'}), 500


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port='5000', debug=True)
    import_rates()

