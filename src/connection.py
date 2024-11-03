import streamlit as st
import psycopg2
from contextlib import contextmanager

@contextmanager
def get_connection(host, port, dbname, user, password):
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        yield conn
    finally:
        if conn:
            conn.close()

def check_connection(host, port, dbname, user, password):
    try:
        with get_connection(host, port, dbname, user, password) as conn:
            return True
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")
        return False

def save_connection_params(host, port, dbname, user, password):
    st.session_state['connection_params'] = {
        'host': host,
        'port': port,
        'dbname': dbname,
        'user': user,
        'password': password
    }
    st.session_state['is_connected'] = True

def connection_page():
    st.subheader("Настройки подключения к базе данных")
    
    # Получаем значения из session_state с дефолтными значениями
    conn_params = st.session_state.get('connection_params', {
        'host': 'localhost',
        'port': 6000,  # Установите порт по умолчанию как строку с числовым значением
        'dbname': '',
        'user': '',
        'password': ''
    })

    host = st.text_input("Host", value=conn_params['host'])
    port = st.text_input("Port", value=conn_params['port'])
    dbname = st.text_input("Database Name", value=conn_params['dbname'])
    user = st.text_input("User", value=conn_params['user'])
    password = st.text_input("Password", type="password", value=conn_params['password'])

    if st.button("Подключиться"):
        st.session_state.connection_params['host'] = host
        st.session_state.connection_params['port'] = port
        st.session_state.connection_params['dbname'] = dbname
        st.session_state.connection_params['user'] = user
        st.session_state.connection_params['password'] = password
        st.session_state.is_connected = True

    if st.button("Проверить соединение"):
        if all([host, port, dbname, user, password]):
            if check_connection(host, port, dbname, user, password):
                save_connection_params(host, port, dbname, user, password)
                st.success("Соединение установлено успешно")
        else:
            st.error("Заполните все поля")
