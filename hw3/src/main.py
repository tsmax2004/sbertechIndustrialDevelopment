from flask import Flask
import psycopg2
import os

app = Flask(__name__)

connection_arguments = {
    "host": os.environ.get('DB_HOST'),
    "database": os.environ.get('POSTGRES_DB'),
    "user": os.environ.get('POSTGRES_USER'),
    "password": os.environ.get('POSTGRES_PASSWORD'),
}


@app.route('/get')
def get():
    try:
        with psycopg2.connect(**connection_arguments) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT counter FROM t_counter;')
                counter = cursor.fetchone()[0]
                return f'Текущее значение: {counter}'
    except Exception as e:
        return f'Ошибка подключения к базе данных: {e}'


@app.route('/inc')
def inc():
    try:
        with psycopg2.connect(**connection_arguments) as conn:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE t_counter SET counter=counter+1 RETURNING counter;')
                counter = cursor.fetchone()[0]
                return f'Текущее значение: {counter}'
    except Exception as e:
        return f'Ошибка подключения к базе данных: {e}'


if __name__ == '__main__':
    with psycopg2.connect(**connection_arguments) as conn:
        with conn.cursor() as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS t_counter (counter INTEGER);')
            cursor.execute('INSERT INTO t_counter VALUES (0);')

    app.run(host='0.0.0.0', port=8080)