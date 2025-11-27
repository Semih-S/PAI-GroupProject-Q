import unittest
import os
import sys

# Add src to path
sys.path.append('src')

from database.db_handler import DatabaseHandler

def simple_test():
    print("🧪 Running simple database test...")
    
    try:
        # Test database connection
        db = DatabaseHandler("test_simple.db")
        print("✅ Database connected")
        
        # Test adding student
        student_id = db.add_student("Test Student", "test@university.com")
        print(f"✅ Student added with ID: {student_id}")
        
        # Test getting students
        students = db.get_all_students()
        print(f"✅ Found {len(students)} students")
        
        # Clean up
        db.close()
        if os.path.exists("test_simple.db"):
            os.remove("test_simple.db")
        
        print("🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    simple_test()
    