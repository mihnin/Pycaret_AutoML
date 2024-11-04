import streamlit as st
import yaml
from yaml.loader import SafeLoader
import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import bcrypt
from ratelimit import limits, sleep_and_retry

FAILED_LOGIN_ATTEMPTS = {}
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 минут

@sleep_and_retry
@limits(calls=MAX_ATTEMPTS, period=LOCKOUT_TIME)
def check_login_attempts(username: str):
    """Проверка количества неудачных попыток входа с rate limiting"""
    if username in FAILED_LOGIN_ATTEMPTS:
        attempts = FAILED_LOGIN_ATTEMPTS[username]
        if datetime.now().timestamp() - attempts['timestamp'] < LOCKOUT_TIME:
            if attempts['attempts'] >= MAX_ATTEMPTS:
                raise Exception("Слишком много попыток. Попробуйте позже.")
        else:
            # Сброс попыток после истечения времени блокировки
            FAILED_LOGIN_ATTEMPTS[username] = {
                'attempts': 0,
                'timestamp': datetime.now().timestamp()
            }

def record_failed_attempt(username: str):
    """Запись неудачной попытки входа"""
    if username not in FAILED_LOGIN_ATTEMPTS:
        FAILED_LOGIN_ATTEMPTS[username] = {
            'attempts': 1,
            'timestamp': datetime.now().timestamp()
        }
    else:
        FAILED_LOGIN_ATTEMPTS[username]['attempts'] += 1
        FAILED_LOGIN_ATTEMPTS[username]['timestamp'] = datetime.now().timestamp()

def load_config():
    """Загрузка конфигурации пользователей"""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.load(file, SafeLoader)
        return config
    except Exception as e:
        st.error(f"Ошибка загрузки конфигурации: {e}")
        return None

def save_config(config):
    """Сохранение конфигурации пользователей"""
    try:
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file)
    except Exception as e:
        st.error(f"Ошибка сохранения конфигурации: {e}")

def init_authenticator():
    """Инициализация аутентификатора"""
    config = load_config()
    if not config:
        return None
    return config

def login():
    """Функция для входа пользователя"""
    config = init_authenticator()
    if not config:
        st.error("Ошибка инициализации аутентификатора.")
        return False

    st.sidebar.header("Вход в систему")
    username = st.sidebar.text_input("Имя пользователя")
    password = st.sidebar.text_input("Пароль", type="password")
    login_button = st.sidebar.button("Войти")

    if login_button:
        if not username or not password:
            st.sidebar.error("Пожалуйста, введите имя пользователя и пароль.")
            return False

        try:
            check_login_attempts(username)
        except Exception as e:
            st.sidebar.error(str(e))
            return False

        user_data = config['credentials']['usernames'].get(username)
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success(f"Добро пожаловать, {user_data['name']}!")
            return True
        else:
            record_failed_attempt(username)
            st.sidebar.error("Имя пользователя или пароль неверны.")
            return False

def register_user(username: str, name: str, password: str, role: str = 'user') -> Tuple[bool, str]:
    """Регистрация нового пользователя с улучшенной валидацией"""
    try:
        is_valid, msg = validate_password(password)
        if not is_valid:
            return False, msg

        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return False, "Недопустимое имя пользователя"

        config = load_config()
        if not config:
            return False, "Ошибка конфигурации"

        if username in config['credentials']['usernames']:
            return False, "Пользователь уже существует"

        if role not in ['user', 'admin']:
            return False, "Недопустимая роль"

        # Безопасное хеширование пароля
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        config['credentials']['usernames'][username] = {
            'name': name,
            'password': hashed_password.decode('utf-8'),
            'role': role
        }

        save_config(config)
        return True, "Пользователь успешно зарегистрирован"

    except Exception as e:
        return False, f"Ошибка при регистрации: {str(e)}"

# Добавить константы для паролей
PASSWORD_MIN_LENGTH = 12
PASSWORD_SPECIAL_CHARS = "!@#$%^&*(),.?\":{}|<>"

def validate_password(password: str) -> Tuple[bool, str]:
    """Проверка сложности пароля"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Пароль должен содержать минимум {PASSWORD_MIN_LENGTH} символов"
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать заглавные буквы"
    if not any(c.islower() for c in password):
        return False, "Пароль должен содержать строчные буквы"
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать цифры"
    if not any(c in PASSWORD_SPECIAL_CHARS for c in password):
        return False, f"Пароль должен содержать специальные символы из набора: {PASSWORD_SPECIAL_CHARS}"
    return True, ""

def check_session_timeout():
    """Проверка таймаута сессии"""
    if 'last_activity' not in st.session_state:
        return False

    timeout = timedelta(minutes=30)
    if datetime.now() - st.session_state['last_activity'] > timeout:
        st.session_state['authenticated'] = False
        return False

    st.session_state['last_activity'] = datetime.now()
    return True

def update_last_activity():
    """Обновление времени последней активности"""
    st.session_state['last_activity'] = datetime.now()