import streamlit as st
import psycopg2
from psycopg2 import Error

# Default connection parameters
DEFAULT_CONFIG = {
    'host': 'localhost',    # локальный хост
    'port': '6000',         # порт 6000
    'database': 'postgres', # база данных postgres
    'user': 'postgres',     # пользователь postgres
    'password': '123'       # пароль 123
}

def init_connection_state():
    if 'db_config' not in st.session_state:
        st.session_state.db_config = DEFAULT_CONFIG.copy()

def try_connection(config):
    try:
        conn = psycopg2.connect(**config)
        conn.close()
        return True, None
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    init_connection_state()
    
    st.title("Database Connection Manager")
    
    page = st.sidebar.selectbox("Select Page", ["Connection Settings", "Table Management"])
    
    if page == "Connection Settings":
        st.header("Database Connection Settings")
        
        # Form for connection settings with default values
        with st.form("connection_form"):
            st.session_state.db_config['host'] = st.text_input("Host", value=DEFAULT_CONFIG['host'])
            st.session_state.db_config['port'] = st.text_input("Port", value=DEFAULT_CONFIG['port'])
            st.session_state.db_config['database'] = st.text_input("Database", value=DEFAULT_CONFIG['database'])
            st.session_state.db_config['user'] = st.text_input("User", value=DEFAULT_CONFIG['user'])
            st.session_state.db_config['password'] = st.text_input("Password", value=DEFAULT_CONFIG['password'], type="password")
            
            if st.form_submit_button("Test Connection"):
                success, error = try_connection(st.session_state.db_config)
                if success:
                    st.success("Successfully connected to database!")
                else:
                    st.error(f"Connection failed: {error}")
    
    elif page == "Table Management":
        st.header("Table Management")
        
        # Test connection before proceeding
        success, error = try_connection(st.session_state.db_config)
        if not success:
            st.error(f"Ошибка подключения к БД: {error}")
            st.error("Пожалуйста, проверьте настройки подключения на странице Connection Settings")
            return
            
        # Table management code here
        try:
            conn = psycopg2.connect(**st.session_state.db_config)
            # ... остальной код для управления таблицами ...
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    main()
