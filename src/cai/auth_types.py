from enum import Enum

class Edition(Enum):
    """
    Edition levels of the CAI framework.
    """
    COMMUNITY = "community"     # Research & Learning
    PROFESSIONAL = "professional" # Enterprise & Production

class Role(Enum):
    """
    User roles for access control.
    """
    USER = "user"       # Standard user
    ADMIN = "admin"     # Administrative user with full access
