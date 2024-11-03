import streamlit as st
import psycopg2
from psycopg2 import Error

# Существующие импорты и код...

# Параметры по умолчанию с непустыми значениями
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': '6000',
    'database': 'postgres',
    'user': 'postgres',
    'password': '123'  # устанавливаем пароль по умолчанию
}

def init_connection_state():
    if 'db_config' not in st.session_state:
        st.session_state.db_config = DEFAULT_CONFIG.copy()
    else:
        # Проверяем и устанавливаем значения по умолчанию для пустых полей
        for key in DEFAULT_CONFIG:
            if not st.session_state.db_config.get(key):
                st.session_state.db_config[key] = DEFAULT_CONFIG[key]

def try_connection(config):
    # Проверяем наличие всех необходимых параметров
    for key in DEFAULT_CONFIG:
        if not config.get(key):
            config[key] = DEFAULT_CONFIG[key]
    
    try:
        conn = psycopg2.connect(**config)
        conn.close()
        return True, None
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

# В существующей функции main() добавить:
def main():
    # ...существующий код...
    
    init_connection_state()
    
    with st.sidebar:
        page = st.selectbox("Select Page", ["Connection Settings", "Table Management", "Other Features"])
        
        if page == "Connection Settings":
            st.header("Database Connection Settings")
            with st.form("connection_form"):
                # Используем значения из session_state или значения по умолчанию
                st.session_state.db_config['host'] = st.text_input(
                    "Host", 
                    value=st.session_state.db_config.get('host') or DEFAULT_CONFIG['host']
                )
                st.session_state.db_config['port'] = st.text_input(
                    "Port", 
                    value=st.session_state.db_config.get('port') or DEFAULT_CONFIG['port']
                )
                st.session_state.db_config['database'] = st.text_input(
                    "Database", 
                    value=st.session_state.db_config.get('database') or DEFAULT_CONFIG['database']
                )
                st.session_state.db_config['user'] = st.text_input(
                    "User", 
                    value=st.session_state.db_config.get('user') or DEFAULT_CONFIG['user']
                )
                st.session_state.db_config['password'] = st.text_input(
                    "Password", 
                    value=st.session_state.db_config.get('password') or DEFAULT_CONFIG['password'],
                    type="password"
                )
                
                if st.form_submit_button("Test Connection"):
                    success, error = try_connection(st.session_state.db_config)
                    if success:
                        st.success("Successfully connected to database!")
                    else:
                        st.error(f"Connection failed: {error}")
    
    # ...остальной существующий код...
