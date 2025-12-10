from enum import Enum


class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    VIEW = "VIEW"  # View sensitive data
    EXPORT = "EXPORT"  # Export data
    IMPORT = "IMPORT"

    def __str__(self):
        return self.value
