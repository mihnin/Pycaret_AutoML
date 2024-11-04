# roles.py
import streamlit as st
from typing import Optional

# Константы для ролей
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'

def set_role(role: str) -> None:
    """Устанавливает роль текущего пользователя"""
    if role not in [ROLE_ADMIN, ROLE_USER]:
        raise ValueError(f"Недопустимая роль: {role}")
    st.session_state['role'] = role

def get_role() -> str:
    """Возвращает роль текущего пользователя"""
    return st.session_state.get('role', ROLE_USER)

def is_admin() -> bool:
    """Проверяет, является ли текущий пользователь администратором"""
    return get_role() == ROLE_ADMIN

def check_table_ownership(table_name: str, username: Optional[str] = None) -> bool:
    """Проверяет, имеет ли пользователь доступ к таблице"""
    if is_admin():
        return True
    
    if not username:
        username = st.session_state.get('username')
        
    if not username:
        return False
        
    # Здесь можно добавить дополнительную логику проверки владения таблицей
    return True

def require_admin(func):
    """Декоратор для проверки прав администратора"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            st.error("Требуются права администратора")
            return None
        return func(*args, **kwargs)
    return wrapper