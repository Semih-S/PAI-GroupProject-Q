from dataclasses import dataclass

# Store key personal and academic identify information
@dataclass
class Student:
    # identifier for each student
    student_id: str
    first_name: str
    lastname: str
    email: str
    password: str
    year: int


    @property
    def full_name(self) -> str:
        # returns the student full name is a readable format
        return f"{self.first_name} {self.lastname}"


