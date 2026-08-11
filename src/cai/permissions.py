from typing import Optional
from cai.config import get_config, get_active_edition
from cai.auth_types import Edition, Role

def has_permission(user_role: Optional[str] = None, required_edition: Edition = Edition.COMMUNITY) -> bool:
    """
    Проверяет, разрешён ли доступ к функции в текущем контексте (роль пользователя + активный выпуск).
    
    - Роль ADMIN всегда имеет полный доступ.
    - Если required_edition равен COMMUNITY, доступ есть у всех.
    - Если required_edition равен PROFESSIONAL, доступ предоставляется если:
        a) Роль пользователя ADMIN
        b) Глобально активный выпуск — PROFESSIONAL
    """
    # Переопределение для администратора
    if user_role == Role.ADMIN.value:
        return True
    
    # Функции Community всегда доступны
    if required_edition == Edition.COMMUNITY:
        return True
    
    # Функции Professional требуют Professional Edition
    if required_edition == Edition.PROFESSIONAL:
        return get_active_edition() == Edition.PROFESSIONAL
        
    return False

def require_professional(user_role: Optional[str] = None):
    """
    Вспомогательная функция для проверки профессионального доступа.
    Вызывает PermissionError если доступ не предоставлен.
    """
    if not has_permission(user_role, Edition.PROFESSIONAL):
        raise PermissionError("Эта функция требует CAI Professional Edition.")
