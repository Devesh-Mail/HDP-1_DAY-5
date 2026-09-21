import ast
import operator
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# DATABASE LOCATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "students.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================
# TOOL 1: GET STUDENT INFORMATION
# ==========================================

@tool
def get_student_info(student_id: str) -> str:
    """
    Get the student's name and department
    using their student ID.
    """

    with get_connection() as conn:

        row = conn.execute(
            """
            SELECT name, department
            FROM students
            WHERE student_id = ?
            """,
            (student_id,)
        ).fetchone()

    if row is None:
        return f"No student was found with ID {student_id}."

    name, department = row

    return (
        f"Student ID: {student_id}\n"
        f"Name: {name}\n"
        f"Department: {department}"
    )


# ==========================================
# TOOL 2: GET STUDENT MARKS
# ==========================================

@tool
def get_student_marks(student_id: str) -> str:
    """
    Get Python, Database, AI and Web marks
    for a student using their student ID.
    """

    with get_connection() as conn:

        row = conn.execute(
            """
            SELECT python, database, ai, web
            FROM students
            WHERE student_id = ?
            """,
            (student_id,)
        ).fetchone()

    if row is None:
        return f"No student was found with ID {student_id}."

    python_mark, database_mark, ai_mark, web_mark = row

    return (
        f"Student ID: {student_id}\n"
        f"Python: {python_mark}\n"
        f"Database: {database_mark}\n"
        f"AI: {ai_mark}\n"
        f"Web: {web_mark}"
    )


# ==========================================
# SAFE CALCULATOR
# ==========================================

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate(node):

    # Number
    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

    # +number / -number
    if isinstance(node, ast.UnaryOp):

        if type(node.op) in _ALLOWED_OPERATORS:

            return _ALLOWED_OPERATORS[type(node.op)](
                _safe_calculate(node.operand)
            )

    # Binary operations
    if isinstance(node, ast.BinOp):

        if type(node.op) in _ALLOWED_OPERATORS:

            left = _safe_calculate(node.left)
            right = _safe_calculate(node.right)

            return _ALLOWED_OPERATORS[type(node.op)](
                left,
                right
            )

    raise ValueError(
        "Only basic arithmetic expressions are allowed."
    )


# ==========================================
# TOOL 3: CALCULATOR
# ==========================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a basic arithmetic expression.

    Examples:
    85+72+90+78
    325/4
    """

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = _safe_calculate(
            tree.body
        )

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return f"{expression} = {result}"

    except Exception as error:

        return (
            f"Could not calculate "
            f"'{expression}': {error}"
        )


# ==========================================
# TOOL 4: GET PASSING RULES
# ==========================================

@tool
def get_passing_rules() -> str:
    """
    Return the university passing rules.
    Minimum overall average is 40 percent.
    Minimum mark in each subject is 35 percent.
    """

    return (
        "University passing rules:\n"
        "1. Minimum overall average: 40%\n"
        "2. Minimum mark in each subject: 35%"
    )


# ==========================================
# LIST OF TOOLS
# ==========================================

tools = [
    get_student_info,
    get_student_marks,
    calculator,
    get_passing_rules
]


# ==========================================
# GEMINI MODEL
# ==========================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0
)


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """

You are a student information assistant.

You have access to four tools:

1. get_student_info
   Use this when the user asks for a student's
   name or department.

2. get_student_marks
   Use this when the user asks for marks.

3. calculator
   Use this when calculations are required,
   such as total marks or average marks.

4. get_passing_rules
   Use this when the user asks about passing
   eligibility or university requirements.

Important rules:

- Do not invent student information.
- Always use the tools when database information
  is required.
- You decide which tools are needed.
- Do NOT follow a hard-coded tool sequence.
- You may call multiple tools.
- A previous tool result can determine whether
  another tool is required.

A student satisfies the passing requirements only if:

1. Overall average >= 40%
2. Every subject mark >= 35%

Give a clear final answer.
"""


# ==========================================
# CREATE AGENT
# ==========================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT
)


# ==========================================
# ASK AGENT
# ==========================================

def ask_agent(question: str) -> str:

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    # Find the final AI response
    for message in reversed(
        result["messages"]
    ):

        if (
            getattr(message, "type", None) == "ai"
            and message.content
        ):

            return (
                message.content
            )

    return "The agent did not return an answer."


# ==========================================
# SHOW TOOL TRACE
# ==========================================

def show_tool_trace(question: str):

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    print("\n========== AGENT TOOL TRACE ==========")

    for message in result["messages"]:

        tool_calls = getattr(
            message,
            "tool_calls",
            None
        )

        if tool_calls:

            for call in tool_calls:

                print(
                    f"Tool selected: "
                    f"{call['name']}"
                )

                print(
                    f"Arguments: "
                    f"{call['args']}"
                )

        if getattr(
            message,
            "type",
            None
        ) == "tool":

            print(
                f"Tool result: "
                f"{message.content}"
            )

    print(
        "======================================\n"
    )


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    print(
        "===================================="
    )

    print(
        " Student Multi-Tool LangChain Agent"
    )

    print(
        "===================================="
    )

    print(
        "Type 'exit' to stop.\n"
    )

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":

            print("Goodbye!")

            break

        if not question:
            continue

        try:

            answer = ask_agent(
                question
            )

            if isinstance(answer, list):
                answer = "\n".join(
                item["text"]
                for item in answer
                if isinstance(item, dict) and item.get("type") == "text"
                )

            print(
                f"\nAgent: {answer}\n"
            )

        except Exception as error:

            print(
                f"\nError: {error}\n"
            )