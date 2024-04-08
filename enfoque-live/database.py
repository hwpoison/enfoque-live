import sqlite3
import configuration

DB_FILENAME = configuration.get("tokens_db_name")


def create_table():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            name TEXT,
            footprint TEXT,
            status TEXT,
            banned BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()


def count_tokens_with_condition(condition):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM tokens WHERE status = ?", (condition,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def token_exists(token):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    conn.commit()
    conn.close()

    return False if existing_token is None else True


def dump_token(token):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tokens WHERE token = ?', (token,))
    result = cursor.fetchone()
    conn.close()

    if result is not None:
        token_data = {
            'token': result[0],
            'name': result[1],
            'footprint': result[2],
            'status': result[3],
            'banned': bool(result[4])
        }
        token_json = token_data  # to json
        return token_json
    else:
        return None


def store_token(token, name, footprint, status, banned):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    if token_exists(token) is False:
        cursor.execute('INSERT INTO tokens (token, name, footprint, status, banned) VALUES (?, ?, ?, ?, ?)',
                       (token, name, footprint, status, banned))
        print(f'Token {token} almacenado exitosamente.')
    else:
        print(f'El token {token} ya existe en la base de datos.')

    conn.commit()
    conn.close()


def retrieve_tokens():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tokens WHERE status != "to_approve"')
    tokens = cursor.fetchall()
    conn.close()
    return {token[0]: {'name': token[1], 'footprint': token[2], 'status': token[3], 'banned': token[4]} for token in tokens}


def ban_token(token):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    if existing_token is not None:
        cursor.execute(
            'UPDATE tokens SET banned = ? WHERE token = ?', (True, token))
        print(f'Token {token} baneado exitosamente.')
    else:
        print(f'El token {token} no existe en la base de datos.')

    conn.commit()
    conn.close()


def set_token_status(token, new_status):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    if existing_token is not None:
        cursor.execute(
            'UPDATE tokens SET status = ? WHERE token = ?', (new_status, token))
        print(f'Token {token} estado actualizado exitosamente.')
    else:
        print(f'El token {token} no existe en la base de datos.')

    conn.commit()
    conn.close()


def unban_token(token):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    if existing_token is not None:
        cursor.execute(
            'UPDATE tokens SET banned = ? WHERE token = ?', (False, token))
        print(f'Token {token} baneado exitosamente.')
    else:
        print(f'El token {token} no existe en la base de datos.')

    conn.commit()
    conn.close()


def delete_token_(token):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    if existing_token is not None:
        print(token)
        cursor.execute('DELETE FROM tokens WHERE token = ?', (token,))
        print(f'Token {token} eliminado exitosamente.')
    else:
        print(f'El token {token} no existe en la base de datos.')

    conn.commit()
    conn.close()

def delete_token_by_alias(alias):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tokens WHERE name = ?', (alias,))
    conn.commit()
    conn.close()

def delete_all_tokens():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS backup')
    cursor.execute('CREATE TABLE backup AS SELECT * FROM tokens')
    cursor.execute('DELETE FROM tokens')
    conn.commit()
    conn.close()

def restore_tokens_from_backup():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO tokens SELECT * FROM backup')
    except sqlite3.Error as e:
        print("Error during backup restoring:", e)
    conn.commit()
    conn.close()

def set_footprint(token, new_footprint):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tokens WHERE token = ?', (token,))
    existing_token = cursor.fetchone()

    if existing_token is not None:
        cursor.execute(
            'UPDATE tokens SET footprint = ? WHERE token = ?', (new_footprint, token))

    conn.commit()
    conn.close()
