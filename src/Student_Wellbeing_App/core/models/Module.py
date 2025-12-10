from dataclasses import dataclass

@dataclass
class Module:
    module_code: str  # Primary Key
    title: str
    
    @property
    def display_name(self) -> str:
        # Returns a user-friendly representation of the module
        return f"{self.module_code}: {self.title}"