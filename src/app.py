import streamlit as st
import logging
from connection import connection_page
from table_management import table_management_page
from sqlalchemy import create_engine
from roles import set_role, get_role, is_admin
from auth import login, check_session_timeout, update_last_activity, register_user
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Добавим проверку сессии и безопасное хранение параметров
def init_session_state():
    """Инициализация состояния сессии"""
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'connection_params' not in st.session_state:
        st.session_state['connection_params'] = {
            'host': 'localhost',
            'port': 6000,  # Фиксированный порт
            'dbname': '',
            'user': '',
            'password': '123'  # Установите пароль 123
        }
    if 'is_connected' not in st.session_state:
        st.session_state['is_connected'] = False
    if 'last_activity' not in st.session_state:
        st.session_state['last_activity'] = datetime.now()

def check_session():
    """Проверка сессии"""
    if 'last_activity' in st.session_state:
        if (datetime.now() - st.session_state['last_activity']).seconds > 1800:
            st.session_state['authenticated'] = False
            return False
    return True

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
    init_session_state()

    if not st.session_state['authenticated']:
        authenticated = login()
        if not authenticated:
            st.stop()

    check_session_timeout()
    update_last_activity()

    # Пример формы регистрации
    st.sidebar.header("Регистрация")
    with st.sidebar.form("register_form"):
        reg_username = st.text_input("Имя пользователя")
        reg_name = st.text_input("Имя")
        reg_password = st.text_input("Пароль", type="password")
        reg_role = st.selectbox("Роль", ["user", "admin"])
        submit_reg = st.form_submit_button("Зарегистрироваться")

        if submit_reg:
            success, message = register_user(reg_username, reg_name, reg_password, reg_role)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)

    # Остальная часть вашего приложения
    st.title("Главная страница")
    # ...

if __name__ == "__main__":
    main()
