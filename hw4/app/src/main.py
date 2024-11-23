import psycopg2
from flask import Flask


app = Flask(__name__)


connection_arguments = {
    "host": 'app_db',
    "database": 'postgres',
    "user": 'postgres',
    "password": 'password',
}


class Storage:
    def init(self):
        with psycopg2.connect(**connection_arguments) as conn:
            with conn.cursor() as cursor:
                cursor.execute('CREATE TABLE IF NOT EXISTS t_counter (counter INTEGER);')
                cursor.execute('INSERT INTO t_counter VALUES (0);')

    def inc(self):
        try:
            with psycopg2.connect(**connection_arguments) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('UPDATE t_counter SET counter=counter+1 RETURNING counter;')
                    counter = cursor.fetchone()[0]
                    return counter
        except Exception as e:
            return f'Ошибка подключения к базе данных: {e}'

    def get(self):
        try:
            with psycopg2.connect(**connection_arguments) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT counter FROM t_counter;')
                    counter = cursor.fetchone()[0]
                    return counter
        except Exception as e:
            return f'Ошибка подключения к базе данных: {e}'


def make_storage(): return Storage()


@app.route('/get')
def get():
    db = make_storage()
    value = db.get()
    return f'Текущее значение: {value}'


@app.route('/inc')
def inc():
    db = make_storage()
    value = db.inc()
    return f'Текущее значение: {value}'


if __name__ == '__main__':
    make_storage().init()
    app.run(host='0.0.0.0', port=8080)
