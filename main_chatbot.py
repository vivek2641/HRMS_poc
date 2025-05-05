from sql_query import query_db
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import List
from chatbot_openai import get_endpoint_response,summarize_user_query
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
    query = """SELECT * FROM employees"""
    return query_db(query)

@app.get("/employee/{employee_id}")
def get_employee_by_id(employee_id: int):
    query = """SELECT ep.*, b.* , l.*, lb.*  FROM employees as ep
               left join birthdays as b on b.employee_id = ep.employee_id
               left join leaves as l on l.employee_id = ep.employee_id
               left join leave_balance as lb on lb.employee_id = ep.employee_id
               WHERE ep.employee_id = %s"""
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
def get_upcoming_birthdays(days: int = 14):
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

@app.get("/employees/department/{employee_id}")
def get_department_by_employee_id(employee_id: str):
    query = """SELECT employee_id,
                      first_name, 
                      last_name, 
                      department FROM employees WHERE employee_id = %s"""
    return query_db(query, (employee_id,))

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

# Base URL for HRMS API
HRMS_BASE_URL = "http://127.0.0.1:8000"

@app.post("/get-data")
def get_data(employee_id: str, endpoint_list: List[str]):
    data = []
    for endpoint in endpoint_list:
        if endpoint.endswith("/"):
            url = f"{HRMS_BASE_URL}{endpoint}{employee_id}"
        else:
            url = f"{HRMS_BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data.append(response.json())
            else:
                print(f"Request to {url} failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
    
    return data

#--------------------------------------------------------------------
# data save in csv 

import csv
import os

# Add this at the top with other imports
CSV_FILE_PATH = "chatbot_logs.csv"

def save_to_csv(employee_id: str, user_query: str, chatbot_response: str, endpoint_list: List[str],url:str):
    """Save the conversation to a CSV file"""
    # Create file with headers if it doesn't exist
    file_exists = os.path.isfile(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["employee_id", "user_query", "chatbot_response","endpoint_list","url"])
            
        writer.writerow([
            employee_id,
            user_query,
            chatbot_response,
            endpoint_list,
            url
        ])

@app.post("/chatbot/query")
def handle_chatbot_query(employee_id: str, user_message: str):
    """
    Handle chatbot queries by:
    1. Determining which endpoints to call based on the user message
    2. Fetching data from those endpoints
    3. Generating a summarized response using OpenAI
    4. Saving the query and response to a CSV file
    """
    endpoint_list = get_endpoint_response(user_message)
    
    if not endpoint_list:
        response_text = "I'm sorry, I don't understand your query."
        save_to_csv(employee_id, user_message, response_text)
        return {"response": response_text}
    
    data = []
    for endpoint in endpoint_list:
        if endpoint.endswith("/"):
            url = f"{HRMS_BASE_URL}{endpoint}{employee_id}"
        else:
            url = f"{HRMS_BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data.append(response.json())
            else:
                print(f"Request to {url} failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
    
    if not data:
        response_text = "I couldn't retrieve any data for your query."
        save_to_csv(employee_id, user_message, response_text)
        return {"response": response_text}
    
    final_response = summarize_user_query(user_message, data)
    save_to_csv(employee_id, user_message, final_response,endpoint_list,url)
    return {"response": final_response}