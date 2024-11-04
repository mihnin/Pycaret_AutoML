import pytest
from src.auth import validate_password, check_login_attempts, FAILED_LOGIN_ATTEMPTS
from datetime import datetime, timedelta

def test_password_validation():
    # Слишком короткий пароль
    is_valid, _ = validate_password("Short1!")
    assert not is_valid
    
    # Без цифр
    is_valid, _ = validate_password("Password!@#")
    assert not is_valid
    
    # Без спецсимволов
    is_valid, _ = validate_password("Password123")
    assert not is_valid
    
    # Валидный пароль
    is_valid, _ = validate_password("ValidPassword123!@#")
    assert is_valid

def test_login_attempts():
    username = "test_user"
    # Очистка предыдущих попыток
    if username in FAILED_LOGIN_ATTEMPTS:
        del FAILED_LOGIN_ATTEMPTS[username]
    
    # Проверка блокировки после MAX_ATTEMPTS
    for _ in range(3):
        record_failed_attempt(username)
    
    with pytest.raises(Exception, match="Слишком много попыток"):
        check_login_attempts(username)
