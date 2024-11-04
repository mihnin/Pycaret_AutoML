import streamlit as st
from contextlib import contextmanager
from typing import Optional, Tuple
import logging
from sqlalchemy import create_engine
import re
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

HOST = os.getenv('DATABASE_HOST')
PORT = os.getenv('DATABASE_PORT')
DBNAME = os.getenv('DATABASE_NAME')
USER = os.getenv('DATABASE_USER')
PASSWORD = os.getenv('DATABASE_PASSWORD')

def encrypt_password(password: str) -> bytes:
    """Шифрование пароля"""
    pass

def decrypt_password(encrypted: bytes) -> str:
    """Расшифровка пароля"""
    pass

def validate_connection_params(host: str, port: str, dbname: str, user: str, password: str) -> Tuple[bool, str]:
    """Валидация параметров подключения"""
    if not all([host, port, dbname, user, password]):
        return False, "Все поля должны быть заполнены"
    
    try:
        port_num = int(port)
        if port_num != 6000:  # Проверка на фиксированный порт
            return False, "Порт должен быть 6000"
    except ValueError:
        return False, "Порт должен быть числом"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', dbname):
        return False, "Недопустимое имя базы данных"
        
    return True, ""

@contextmanager
def get_connection(host: str, port: int, dbname: str, user: str, password: str):
    """Контекстный менеджер для подключения к БД"""
    engine = None
    try:
        # Добавляем SSL и таймаут
        connection_url = (
            f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
            '?sslmode=require&connect_timeout=10'
        )
        engine = create_engine(connection_url)
        yield engine
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise
    finally:
        if engine:
            engine.dispose()

def check_connection(host: str, port: int, dbname: str, user: str, password: str) -> Tuple[bool, Optional[str]]:
    """Проверка подключения с возвратом статуса и сообщения об ошибке"""
    try:
        with get_connection(host, port, dbname, user, password) as engine:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
        return True, None
    except Exception as e:
        logger.error(f"Ошибка проверки подключения: {e}")
        return False, str(e)

def save_connection_params(host: str, port: int, dbname: str, user: str, password: str) -> None:
    try:
        # Добавить проверку SSL
        ssl_mode = 'require'  # или 'verify-full' для большей безопасности
        
        connection_url = (
            f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
            f'?sslmode={ssl_mode}'
        )
        
        st.session_state['connection_params'] = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
            'ssl_mode': ssl_mode
        }
        st.session_state['is_connected'] = True
    except Exception as e:
        logger.error(f"Failed to save connection params: {e}")
        raise

def connection_page():
    """Страница настроек подключения"""
    st.subheader("Настройки подключения к базе данных")
    
    # Получаем значения из session_state с дефолтными значениями
    conn_params = st.session_state.get('connection_params', {
        'host': 'localhost',
        'port': 6000,
        'dbname': '',
        'user': '',
        'password': ''
    })

    host = st.text_input("Host", value=conn_params['host'])
    port = st.text_input("Port", value=conn_params['port'])
    dbname = st.text_input("Database Name", value=conn_params['dbname'])
    user = st.text_input("User", value=conn_params['user'])
    password = st.text_input("Password", type="password", value=conn_params['password'])

    if st.button("Проверить соединение"):
        valid, error_msg = validate_connection_params(host, port, dbname, user, password)
        if not valid:
            st.error(error_msg)
            return
            
        success, error = check_connection(host, int(port), dbname, user, password)
        if success:
            st.success("✅ Соединение установлено успешно")
            # Сохраняем параметры подключения
            st.session_state.connection_params = {
                'host': host,
                'port': port,
                'dbname': dbname,
                'user': user,
                'password': password
            }
            st.session_state.is_connected = True
        else:
            st.error(f"❌ Ошибка подключения: {error}")
