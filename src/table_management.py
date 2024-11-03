import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import contextlib
import re
from typing import Optional
import io

@contextlib.contextmanager
def create_db_engine(host, port, dbname, user, password):
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')
    try:
        yield engine
    finally:
        engine.dispose()

def is_valid_table_name(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))

def load_large_csv(file_obj, chunksize=10000):
    chunks = pd.read_csv(file_obj, chunksize=chunksize)
    return pd.concat(chunks)

def save_dataframe_to_db(df: pd.DataFrame, table_name: str, engine, if_exists='replace'):
    # Определяем типы данных
    dtype_mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'object': 'TEXT',
        'datetime64[ns]': 'TIMESTAMP',
        'bool': 'BOOLEAN'
    }
    
    column_types = {col: dtype_mapping.get(str(dtype), 'TEXT') 
                   for col, dtype in df.dtypes.items()}
    
    df.to_sql(table_name, engine, if_exists=if_exists, 
              index=False, dtype=column_types)

def table_management_page(engine):
    st.title("Управление таблицами")
    
    try:
        # Используем напрямую engine вместо создания нового
        tab1, tab2 = st.tabs(["Загрузка данных", "Управление таблицами"])
        
        with tab1:
            handle_data_upload(engine)
        
        with tab2:
            handle_table_management(engine)
    except Exception as e:
        st.error(f"❌ Ошибка при подключении к базе данных: {e}")

def handle_data_upload(engine):
    st.header("Загрузка данных из CSV")
    uploaded_file = st.file_uploader("📂 Выберите CSV файл", type="csv")
    
    if uploaded_file:
        try:
            with st.spinner("Загрузка данных..."):
                data = load_large_csv(uploaded_file)
            st.success("✅ Файл загружен")
            st.dataframe(data.head())
            
            table_name = st.text_input("Имя таблицы")
            if table_name and not is_valid_table_name(table_name):
                st.error("Недопустимое имя таблицы")
                return
            
            if st.button("💾 Сохранить", type="primary", disabled=not table_name):
                with st.spinner("Сохранение..."):
                    save_dataframe_to_db(data, table_name, engine)
                st.success("✅ Сохранено")
        except Exception as e:
            st.error(f"Ошибка: {e}")

def handle_table_management(engine):
    st.header("Управление существующими таблицами")
    
    # Получаем список существующих таблиц
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        tables = pd.read_sql(query, engine)['table_name'].tolist()
        
        if tables:
            selected_table = st.selectbox("Выберите таблицу", tables)
            
            if selected_table:
                # Загружаем данные выбранной таблицы
                query = f"SELECT * FROM {selected_table}"
                df = pd.read_sql(query, engine)
                
                # Показываем данные в редактируемой таблице
                st.subheader(f"Данные таблицы: {selected_table}")
                edited_df = st.data_editor(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Сохранить изменения"):
                        try:
                            edited_df.to_sql(selected_table, engine, if_exists='replace', index=False)
                            st.success("✅ Изменения сохранены")
                        except Exception as e:
                            st.error(f"❌ Ошибка при сохранении: {e}")
                
                with col2:
                    if st.button("🗑️ Удалить таблицу"):
                        try:
                            with engine.connect() as conn:
                                conn.execute(f"DROP TABLE {selected_table}")
                            st.success(f"✅ Таблица {selected_table} удалена")
                        except Exception as e:
                            st.error(f"❌ Ошибка при удалении: {e}")
        else:
            st.info("📝 Нет доступных таблиц. Загрузите данные на вкладке 'Загрузка данных'")
    except Exception as e:
        st.error(f"❌ Ошибка при получении списка таблиц: {e}")
