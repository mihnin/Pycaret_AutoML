import pytest
from src.connection import check_connection, validate_connection_params

# Тестовые параметры подключения
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': '6000',
    'dbname': 'test_db',
    'user': 'test_user',
    'password': 'test_password'
}

def test_invalid_connection():
    config = DEFAULT_CONFIG.copy()
    config['port'] = '9999'
    valid, _ = validate_connection_params(**config)
    assert not valid

def test_invalid_credentials():
    config = DEFAULT_CONFIG.copy()
    success, _ = check_connection(
        config['host'],
        int(config['port']),
        config['dbname'],
        config['user'],
        'wrong_password'
    )
    assert not success

def test_invalid_host():
    config = DEFAULT_CONFIG.copy()
    success, _ = check_connection(
        'invalid_host',
        int(config['port']),
        config['dbname'],
        config['user'],
        config['password']
    )
    assert not success

def test_empty_database():
    config = DEFAULT_CONFIG.copy()
    valid, _ = validate_connection_params(
        config['host'],
        config['port'],
        '',
        config['user'],
        config['password']
    )
    assert not valid
