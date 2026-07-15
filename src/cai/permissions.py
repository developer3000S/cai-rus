from typing import Optional
from cai.config import get_config, get_active_edition
from cai.auth_types import Edition, Role

def has_permission(user_role: Optional[str] = None, required_edition: Edition = Edition.COMMUNITY) -> bool:
    """
    Check if the current context (user role + active edition) allows access to a feature.
    
    - ADMIN role always has full access.
    - If required_edition is COMMUNITY, everyone has access.
    - If required_edition is PROFESSIONAL, access is granted if:
        a) User role is ADMIN
        b) The global active edition is PROFESSIONAL
    """
    # Admin override
    if user_role == Role.ADMIN.value:
        return True
    
    # Community features are always available
    if required_edition == Edition.COMMUNITY:
        return True
    
    # Professional features require Professional Edition
    if required_edition == Edition.PROFESSIONAL:
        return get_active_edition() == Edition.PROFESSIONAL
        
    return False

def require_professional(user_role: Optional[str] = None):
    """
    Helper to check if professional access is granted.
    Raises PermissionError if not.
    """
    if not has_permission(user_role, Edition.PROFESSIONAL):
        raise PermissionError("This feature requires CAI Professional Edition.")
