import streamlit as st
import logging
from connection import connection_page
from table_management import table_management_page
from sqlalchemy import create_engine
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def init_session_state():
    """Инициализация состояния сессии"""
    if 'is_connected' not in st.session_state:
        st.session_state['is_connected'] = False
    if 'connection_params' not in st.session_state:
        st.session_state['connection_params'] = {
            'host': 'localhost',
            'port': 6000,  # Установите порт по умолчанию как строку с числовым значением
            'dbname': 'postgres',
            'user': 'postgres',
            'password': '123'
        }

def create_engine_from_session():
    """Создание engine из параметров сессии"""
    try:
        params = st.session_state.connection_params
        logger.info(f"Параметры подключения: {params}")
        port = int(params['port'])  # Преобразуем порт в целое число
        return create_engine(
            f"postgresql://{params['user']}:{params['password']}@"
            f"{params['host']}:{port}/{params['dbname']}"
        )
    except Exception as e:
        logger.error(f"Ошибка создания engine: {e}")
        st.error("Ошибка подключения к БД")
        return None

def main():
    try:
        # Переместили инициализацию в начало
        init_session_state()
        
        st.title("CSV to PostgreSQL Loader")
        
        page = st.sidebar.selectbox(
            "Навигация", 
            ["Настройки подключения", "Управление таблицами"]
        )

        if page == "Настройки подключения":
            connection_page()
        elif page == "Управление таблицами":
            if st.session_state.is_connected:
                engine = create_engine_from_session()
                if engine:
                    table_management_page(engine)
            else:
                st.error("Настройте подключение")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        st.error("Произошла ошибка. Проверьте логи.")

if __name__ == "__main__":
    main()
