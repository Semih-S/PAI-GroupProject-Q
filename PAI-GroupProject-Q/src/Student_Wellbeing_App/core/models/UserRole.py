from enum import Enum


class UserRole(str, Enum):
    WELLBEING_OFFICER = "WELLBEING_OFFICER"
    COURSE_DIRECTOR = "COURSE_DIRECTOR"
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
