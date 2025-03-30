from sqlite3 import Connection
import sqlite3 as sql


# Функция для подключения к базе данных, если базы с переданным именем нет, он создаст ее сам
def connection_for_db(name: str = 'currency.db') -> Connection:
    return sql.connect(f"../database/{name}")


# Класс для удобной работы с базой данных в коде
class DataBase:
    def __init__(self, database_connection: Connection):
        self.connection = database_connection

    def create_table(self, table: str) -> bool:
        try:
            with self.connection as con:
                con.cursor().execute(f"""CREATE TABLE IF NOT EXISTS '{table}' (
                currency TEXT PRIMARY KEY,
                rate REAL
                )""")
                return True

        except Exception as e:
            print(repr(e))
            return False

    def delete_table(self, table: str) -> bool:
        try:
            with self.connection as con:
                con.cursor().execute(f"DROP TABLE {table}")
                return True

        except Exception as e:
            print(repr(e))
            return False

    def clear_table(self, table: str) -> bool:
        try:
            with self.connection as con:
                con.cursor().execute(f"DELETE FROM {table}")
                return True

        except Exception as e:
            print(repr(e))
            return False

    def input_for_database(self, table: str, currency: str, rate: float) -> bool:
        try:
            with self.connection as con:
                con.cursor().execute(f"INSERT INTO {table} (currency, rate) VALUES(?, ?)", (currency, rate))
                return True
        except Exception as e:
            print(repr(e))
            return False

    def select_for_database(self, table: str) -> list:
        try:
            with self.connection as con:
                result = con.cursor().execute(f"SELECT * FROM {table}").fetchall()
                return result

        except Exception as e:
            print(repr(e))
            return [None]

    def update_for_database(self, table: str, currency: str, rate: float) -> bool:
        try:
            with self.connection as con:
                con.cursor().execute(f"UPDATE {table} SET rate = ? WHERE currency = ?", (rate, currency))

        except Exception as e:
            print(repr(e))
            return False
