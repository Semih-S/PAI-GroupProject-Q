# Student Wellbeing Management System

## Project Overview
A Python-based student wellbeing management system providing complete functionality for student information management, attendance tracking, wellbeing records, and alert systems.

## Environment Setup

### 1. Clone Project
```bash
git clone https://github.com/Semih-S/PAI-GroupProject-Q.git
cd PAI-GroupProject-Q/PAI-GroupProject-Q
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Development (SQLite)
System uses SQLite by default. No additional configuration needed. Database file will be created at:
```
PAI-GroupProject-Q\PAI-GroupProject-Q\src\Student_Wellbeing_App\core\database\student_wellbeing_db.sqlite3
```

### 5. Initialize Database
```bash
# Run database migrations
python -m src.Student_Wellbeing_App.core.database.migrations

# Optional: Seed test data
# default password: password123
python -m src.Student_Wellbeing_App.core.database.SeedData

# Optional: Delete database 
python -m src.Student_Wellbeing_App.core.database.WipeDatabase
# You can run 'python -m src.database.migrations' to generate a new one
```


## Launch Application

### Web Interface (Streamlit)
```bash
streamlit run src/Student_Wellbeing_App/core/streamlit_UI/app.py
```
Application opens in browser at: http://localhost:8501

## Run Tests
```
 pytest src/Student_Wellbeing_App/tests/test_wellbeing_service.py
```

