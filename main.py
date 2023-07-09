from fastapi import FastAPI, HTTPException, Request, Depends #Depends voinee poistaa
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi #ei tarpeellinen
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import sqlite3
import random
import string
import configparser

#---------------------- THIS SECTION IS FOR GENERATING THE DATABASE ----------------------
# Check if the `employee.db` file exists and delete it if it does
if os.path.exists("employee.db"):
    os.remove("employee.db")

# Define a function to create the apikeys table and populate it with random API keys
def create_apikeys_table():
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()

    # Create the apikeys table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS apikeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid TEXT NOT NULL
        )
        """
    )

    # Generate 4 random API keys
    api_keys = []
    for _ in range(4):
        api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        api_keys.append(api_key)

    # Insert the API keys into the table
    cursor.executemany("INSERT INTO apikeys (appid) VALUES (?)", [(key,) for key in api_keys])
    conn.commit()

    print("API keys table created and populated.")

# Call the function to create the apikeys table
create_apikeys_table()

# Load first names, last names, road names, and cities from the INI file
config = configparser.ConfigParser()
config.read("employee_data.ini")

first_names = config["Data"]["FirstNames"].split("\n")
last_names = config["Data"]["LastNames"].split("\n")
road_names = config["Data"]["RoadNames"].split("\n")
cities = config["Data"]["Cities"].split("\n")

# Generate a random 5-digit zip code
def generate_zip_code():
    return str(random.randint(10000, 99999))

# Generate a random American telephone number
def generate_telephone_number():
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

# Generate a random company email
def generate_company_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}@company.com"

# Generate random employees data
def generate_employees_data():
    employees_data = []

    num_employees = random.randint(20, 60)

    existing_ids = set()

    for _ in range(num_employees):
        employee_id = random.randint(1, 200)
        while employee_id in existing_ids:  # Ensure unique employee IDs
            employee_id = random.randint(1, 200)
        existing_ids.add(employee_id)

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        address = f"{random.randint(1, 999)} {random.choice(road_names)}"
        city = random.choice(cities)
        zip_code = generate_zip_code()
        telephone = generate_telephone_number()
        company_email = generate_company_email(first_name, last_name)

        employee_data = (employee_id, first_name, last_name, address, city, zip_code, "USA", telephone, company_email)
        employees_data.append(employee_data)

    return employees_data

# Create the employees table and populate it with random employee data
def create_employees_table():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    # Create the employees table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            city TEXT,
            zip TEXT,
            country TEXT,
            telephone TEXT,
            company_email TEXT
        )
        """
    )

    employees_data = generate_employees_data()

    # Insert the employee data into the table
    cursor.executemany(
        "INSERT INTO employees (id, first_name, last_name, address, city, zip, country, telephone, company_email) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        employees_data,
    )

    conn.commit()

    print("employees table created and employees added to the table.")

# Call the function to create the employees table and populate it with random data
create_employees_table()

# Generate a random string of lowercase letters and digits
def generate_random_string(length):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Create the banking_details table
def create_banking_details_table():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    # Create the banking_details table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS banking_details (
            id INTEGER PRIMARY KEY,
            bank_account TEXT,
            bic_swift TEXT
        )
        """
    )

    # Populate the banking_details table with random data for each employee ID
    cursor.execute("SELECT id FROM employees")
    employee_ids = cursor.fetchall()

    banking_data = []

    for employee_id in employee_ids:
        bank_account = str(random.randint(10**9, 10**12 - 1))
        bic_swift = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        banking_data.append((employee_id[0], bank_account, bic_swift))

    cursor.executemany(
        "INSERT INTO banking_details (id, bank_account, bic_swift) VALUES (?, ?, ?)",
        banking_data,
    )

    conn.commit()

    print(f"Banking details table created records added to the table.")

# Create the single_row_table with a random name
def create_single_row_table():
    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    #SQL database table names should not start with numbers
    first_character = random.choice(string.ascii_lowercase)

    table_name = first_character + generate_random_string(11)

    # Create the single_row_table if it doesn't exist
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            data TEXT
        )
        """
    )

    # Generate a random string of 24 characters
    data = generate_random_string(24)

    # Insert the single row into the single_row_table
    cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (data,))

    conn.commit()

    print(f"A single row added to the randomly named table.")

# Call the functions to create the new tables
create_banking_details_table()
create_single_row_table()

#----------------------------- THIS SECTION IS FOR THE API -------------------------------
app = FastAPI(
    title="Vuln HRMS 1.0 - SQL Injection Training Site",
    description="Vuln HRMS 1.0 is a training site designed to simulate SQL injection vulnerabilities. It stores employee information using SQLite database and provides an API for retrieving employee details. This API documentation provides information about the available endpoints and their usage.",
    version="1.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Define a model for the employee entity
class Employee(BaseModel):
    id: str
    first_name: str
    last_name: str
    address: str
    city: str
    zip: str
    country: str
    telephone: str
    company_email: str

# Define a model for the employee banking details
class Banking(BaseModel):
    id: str
    bank_account: str
    bic_swift: str

# Define a function to establish a connection with the database
def get_connection():
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define an API endpoint to get the number of employees
@app.get("/data/1.0/employees", tags=["Employees"])
def get_employee_count():
    """
    Get the number of employees.

    This endpoint allows you to retrieve the total number of employees in the employees table.

    Returns the count of employees as JSON.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Execute SQL query to get the count of employees
    cursor.execute("SELECT COUNT(*) AS employee_count FROM employees")
    row = cursor.fetchone()

    employee_count = row["employee_count"]

    return JSONResponse(content={"employee_count": employee_count})

# Define an API endpoint for retrieving employee details by ID
@app.get("/data/1.0/call/contact", tags=["Employees"])
def get_employee(employee_id: str, appid: str):
    """
    Retrieve employee details by ID.

    This endpoint allows you to retrieve the details of one or more employees by their IDs.
    You need to provide a valid API key (`appid`) to authenticate the request.

    - **employee_id**: IDs of the employees to retrieve, separated by commas.
    - **appid**: API key (24 characters) for authentication.

    Returns the employee information as JSON.
    """
    # Perform API key validation
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM apikeys WHERE appid = '{appid}'")
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Prepare the SQL query with multiple employee IDs
    cursor.execute(f"SELECT * FROM employees WHERE id IN ({employee_id})")
    rows = cursor.fetchall()

    employees = []
    for row in rows:
        employee = Employee(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            address=row["address"],
            city=row["city"],
            zip=row["zip"],
            country=row["country"],
            telephone=row["telephone"],
            company_email=row["company_email"]
        )
        employees.append(employee)

    if not employees:
        raise HTTPException(status_code=404, detail="No employees found")

    return JSONResponse(content=[employee.dict() for employee in employees])

# Define an API endpoint for retrieving employee banking details by employee ID
@app.get("/data/1.0/call/banking", tags=["Employees"])
def get_employee_banking(employee_id: str, appid: str):
    """
    Retrieve employee banking details by employee ID.

    This endpoint allows you to retrieve the banking details of one or more employees by their IDs.
    You need to provide a valid API key (`appid`) to authenticate the request.

    - **employee_id**: IDs of the employees to retrieve, separated by commas.
    - **appid**: API key (24 characters) for authentication.

    Returns the employee information as JSON.
    """
    # Perform API key validation
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM apikeys WHERE appid = '{appid}'")
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Prepare the SQL query with multiple employee IDs
    cursor.execute(f"SELECT * FROM banking_details WHERE id IN ({employee_id})")
    rows = cursor.fetchall()

    bankings = []
    for row in rows:
        banking = Banking(
            id=row["id"],
            bank_account=row["bank_account"],
            bic_swift=row["bic_swift"]
        )
        bankings.append(banking)
    
    if not bankings:
        raise HTTPException(status_code=404, detail="No banking details found")
    
    return JSONResponse(content=[banking.dict() for banking in bankings])

# Generate OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

#---------------------------- THIS SECTION IS FOR THE GAME -------------------------------
# Get correct answers from the database
conn = get_connection()
cursor = conn.cursor()

# Question 1
def question1_answer():
    cursor.execute("SELECT COUNT(*) FROM employees")
    row = cursor.fetchone()
    return str(row[0])

def question2_answer():
    cursor.execute("SELECT id FROM employees ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    random_id = row[0]
    cursor.execute("SELECT first_name, last_name FROM employees WHERE id = ?", (random_id,))
    row = cursor.fetchone()
    answer2 = row[0] + " " + row[1]
    return answer2, random_id

def question3_answer():
    cursor.execute("SELECT name FROM sqlite_schema WHERE name NOT IN ('apikeys', 'sqlite_sequence', 'employees', 'banking_details')")
    row = cursor.fetchone()
    return str(row[0])

def question4_answer():
    table = question3_answer()
    cursor.execute(f"SELECT data FROM {table}")
    row = cursor.fetchone()
    return str(row[0])

# Dictionary to store the questions and correct answers
answer1 = question1_answer()
answer2, random_id = question2_answer()
answer3 = question3_answer()
answer4 = question4_answer()

questions = [
    {
        "question": "What is the number of employees in the database?",
        "correct_answer": answer1,
        "hints": ["You will find the necessary query from /docs"],
        "hint_index": 0,
        "correct": False
    },
    {
        "question": f"What is the first and last name of  the employee whose id is {random_id}?",
        "correct_answer": answer2,
        "hints": ["Appid is first checked from the query parameters", "The SQL query is as follows: ...WHERE appid = '{variable}'"],
        "hint_index": 0,
        "correct": False
    },
    {
        "question": "There is one strange-looking table in the database, what is its name?",
        "correct_answer": answer3,
        "hints": ["It is probably easier to use /data/1.0/call/banking query", "Try sqlite_schema table or similar", "One word: UNION"],
        "hint_index": 0,
        "correct": False
    },
    {
        "question": "What is the flag found in that table?",
        "correct_answer": answer4,
        "hints": ["Again sqlite_schema table or similar may help"],
        "hint_index": 0,
        "correct": False
    }
]

def default_settings():
    for question in questions:
        question["hint_index"] = 0
        question["correct"] = False

def is_final():
    number_correct = 0
    for question in questions:
        if question["correct"] is True:
            number_correct += 1
    return number_correct

@app.get("/", include_in_schema=False)
async def index(request: Request):
    default_settings()
    return templates.TemplateResponse("index.html", {"request": request, "questions": questions})

@app.post("/answers/{question_idx}", include_in_schema=False)
async def answers(question_idx: int, answer: str):
    question_index = question_idx - 1
    question = questions[question_index]
    is_correct = question["correct_answer"].lower() == answer.lower()
    if is_correct is True:
        question["correct"]=True
    is_final_bool = is_final() == len(questions)
    return {"answer": answer, "correct": is_correct, "final": is_final_bool}

@app.get("/hints/{question_idx}", include_in_schema=False)
async def get_hint(question_idx: int):
    question_index = question_idx - 1
    question = questions[question_index]

    hint_index = question["hint_index"]
    hints = question["hints"]

    if hint_index >= len(hints):
        return {"hint": None, "last": True}

    hint = hints[hint_index]
    question["hint_index"] += 1

    if hint_index == len(hints) - 1:
        return {"hint": hint, "last": True}
    else:
        return {"hint": hint, "last": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)