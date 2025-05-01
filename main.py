from sql_query import query_db
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional, List, Dict, Any
# from chatbot import chat_with_model
# from chatbot.ChatBot import generate_response, get_chat_history

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
# --- API Endpoints ---

@app.get("/employees")
def get_all_employees():
    query = "SELECT * FROM employees"
    return query_db(query)

@app.get("/employee/{employee_id}")
def get_employee_by_id(employee_id: int):
    query = "SELECT * FROM employees WHERE employee_id = %s"
    return query_db(query, (employee_id,))

@app.get("/birthdays/this-month")
def get_birthdays_this_month():
    query = """
        SELECT e.*, b.birth_date FROM employees e
        JOIN birthdays b ON e.employee_id = b.employee_id
        WHERE MONTH(b.birth_date) = MONTH(CURDATE())
    """
    return query_db(query)

@app.get("/birthdays/upcoming")
def get_upcoming_birthdays(days: int = 7):
    query = """
        SELECT e.*, b.birth_date 
        FROM employees e
        JOIN birthdays b ON e.employee_id = b.employee_id
        WHERE 
            DATE_FORMAT(b.birth_date, '%m-%d') BETWEEN 
                DATE_FORMAT(CURDATE(), '%m-%d') AND 
                DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL %s DAY), '%m-%d')
        ORDER BY DATE_FORMAT(b.birth_date, '%m-%d')
    """
    return query_db(query, (days,))

@app.get("/leave/employee/{employee_id}")
def get_leave_records(employee_id: int):
    query = "SELECT * FROM leaves WHERE employee_id = %s"
    return query_db(query, (employee_id,))

@app.get("/employees/department")
def get_employees_by_department(department: str):
    if not department.isalpha():  
        raise HTTPException(status_code=400, detail="Invalid department name")
    query = "SELECT * FROM employees WHERE department = %s"
    try:
        return query_db(query, (department,))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/leave/today")
def get_employees_on_leave_today():
    query = """
        SELECT e.* FROM employees e
        JOIN leaves l ON e.employee_id = l.employee_id
        WHERE CURDATE() BETWEEN l.start_date AND l.end_date
    """
    return query_db(query)

@app.get("/employees/status-count")
def get_employee_status_count():
    query = "SELECT is_active, COUNT(*) as count FROM employees GROUP BY is_active"
    return query_db(query)

@app.get("/employees/recent-joiners")
def get_recent_joiners():
    query = "SELECT * FROM employees WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    return query_db(query)

@app.get("/leave/no-leave-this-year")
def get_employees_with_no_leave():
    query = """
        SELECT * FROM employees WHERE employee_id NOT IN (
            SELECT DISTINCT employee_id FROM leaves
            WHERE YEAR(start_date) = YEAR(CURDATE())
        )
    """
    return query_db(query)

@app.get("/leave-balances/{employee_id}")
def get_leave_balance(employee_id: int):
    query = """
        SELECT 
            e.first_name,
            e.last_name,
            lb.Casual,
            lb.Sick, 
            lb.Unpaid, 
            lb.Adjustment, 
            lb.total 
        FROM leave_balance lb
        JOIN employees e ON lb.employee_id = e.employee_id
        WHERE lb.employee_id = %s
    """
    result = query_db(query, (employee_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result[0]

# user_input = str(input("Enter your query: "))
# endpoint_list = chat_with_model(user_input)



# #---------------------------------------------

HRMS_BASE_URL = "http://127.0.0.1:8000"


@app.post("/get-data")
def get_data(employee_id: str, endpoint_list: List[str]):
    data = []
    for endpoint in endpoint_list:
        if endpoint.endswith("/"):
            url = f"{HRMS_BASE_URL}{endpoint}{employee_id}"
        else:
            url = f"{HRMS_BASE_URL}{endpoint}"

    print(url,type(url))
    response = requests.get(url)
    print(response)
    data.append(response.json())
    print(data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None
