"""RBAC 角色权限定义"""
ROLES = {
    "reader": {"can_read": True, "can_write_bookshelf": True, "can_create_book": False, "can_delete_book": False},
    "author": {"can_read": True, "can_write_bookshelf": True, "can_create_book": True, "can_delete_book": False},
    "admin": {"can_read": True, "can_write_bookshelf": True, "can_create_book": True, "can_delete_book": True},
}

def check_permission(role: str, permission: str) -> bool:
    return ROLES.get(role, {}).get(permission, False)
