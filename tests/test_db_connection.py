import pytest
from src.streamlit_app import try_connection, DEFAULT_CONFIG

def test_invalid_connection():
    config = DEFAULT_CONFIG.copy()
    config['port'] = '9999'  # Invalid port
    success, error = try_connection(config)
    assert not success
    assert error is not None

def test_invalid_credentials():
    config = DEFAULT_CONFIG.copy()
    config['password'] = 'wrong_password'
    success, error = try_connection(config)
    assert not success
    assert error is not None

def test_invalid_host():
    config = DEFAULT_CONFIG.copy()
    config['host'] = 'invalid_host'
    success, error = try_connection(config)
    assert not success
    assert error is not None

def test_empty_database():
    config = DEFAULT_CONFIG.copy()
    config['database'] = ''
    success, error = try_connection(config)
    assert not success
    assert error is not None
