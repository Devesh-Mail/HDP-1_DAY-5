# Student Multi-Tool LangChain Agent

This project implements a LangChain Agent using Gemini
to answer student-related questions.

The system uses:

- SQLite
- LangChain
- Gemini
- Python
- LangChain Tools

---

## Project Structure

student_multitool_agent/

    main.py

    init_db.py

    students.db

    requirements.txt

    .env

    .env.example

    .gitignore

    README.md


---

# 1. Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv #only once in a lifetime

.venv\Scripts\Activate.ps1 # activating env variable

#2 To install requirements

pip install -r requirements.txt

#3 creating database

python init_db.py

#4 configure api key 

GOOGLE_API_KEY=your_actual_gemini_api_key -> put your gemini api key here in the env file

#5 running agent

python main.py

#6 toots used

get_student_info(student_id)
get_student_marks(student_id)
calculator(expression)
get_passing_rules()
