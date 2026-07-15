import os
from cai.config import get_config, get_active_edition
from cai.auth_types import Edition, Role
from cai.permissions import has_permission

def test_edition_detection():
    print("Testing Edition Detection...")
    
    # Test Community (License Off)
    os.environ["CAI_LICENSE_OFF"] = "1"
    os.environ["ALIAS_API_KEY"] = "some-key"
    # Reset config singleton for testing
    import cai.config
    cai.config.reset_config()
    print(f"  License Off -> {get_active_edition()}")
    assert get_active_edition() == Edition.COMMUNITY
    
    # Test Professional (Valid Key)
    os.environ["CAI_LICENSE_OFF"] = "0"
    os.environ["ALIAS_API_KEY"] = "valid-key"
    cai.config.reset_config()
    print(f"  Valid Key -> {get_active_edition()}")
    assert get_active_edition() == Edition.PROFESSIONAL
    
    # Test Community (No Key)
    os.environ["ALIAS_API_KEY"] = ""
    cai.config.reset_config()
    print(f"  No Key -> {get_active_edition()}")
    assert get_active_edition() == Edition.COMMUNITY

def test_permissions():
    print("\nTesting Permissions...")
    
    # Case 1: Admin role should always have access
    print(f"  Admin role access: {has_permission(user_role=Role.ADMIN.value, required_edition=Edition.PROFESSIONAL)}")
    assert has_permission(user_role=Role.ADMIN.value, required_edition=Edition.PROFESSIONAL) is True
    
    # Case 2: Community edition, normal user -> No Professional access
    os.environ["CAI_LICENSE_OFF"] = "1"
    print(f"  Community edition, user role access: {has_permission(user_role=Role.USER.value, required_edition=Edition.PROFESSIONAL)}")
    assert has_permission(user_role=Role.USER.value, required_edition=Edition.PROFESSIONAL) is False
    
    # Case 3: Professional edition, normal user -> Professional access
    os.environ["CAI_LICENSE_OFF"] = "0"
    os.environ["ALIAS_API_KEY"] = "valid-key"
    print(f"  Professional edition, user role access: {has_permission(user_role=Role.USER.value, required_edition=Edition.PROFESSIONAL)}")
    assert has_permission(user_role=Role.USER.value, required_edition=Edition.PROFESSIONAL) is True

if __name__ == "__main__":
    try:
        test_edition_detection()
        test_permissions()
        print("\nAll basic edition/permission tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)
