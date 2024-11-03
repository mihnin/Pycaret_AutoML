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
        'port': dbname,
        'dbname': dbname,
        'user': user,
        'password': password
    }
    st.session_state['is_connected'] = True

def connection_page():
    st.subheader("Настройки подключения к базе данных")
    
    # Получаем значения из session_state с дефолтными значениями
    conn_params = st.session_state['connection_params']

    host = st.text_input("Хост", value=conn_params['host'])
    port = st.text_input("Порт", value=conn_params['port'])
    dbname = st.text_input("Имя базы данных", value=conn_params['dbname'])
    user = st.text_input("Пользователь", value=conn_params['user'])
    password = st.text_input("Пароль", type="password", value=conn_params['password'])

    if st.button("Проверить соединение"):
        if all([host, port, dbname, user, password]):
            if check_connection(host, port, dbname, user, password):
                save_connection_params(host, port, dbname, user, password)
                st.success("Соединение установлено успешно")
        else:
            st.error("Заполните все поля")
