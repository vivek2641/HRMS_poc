from fastapi import FastAPI
from sql_query import query_db

app = FastAPI()

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
        SELECT e.*, b.birth_date, b.upcoming_birthday FROM employees e
        JOIN birthdays b ON e.employee_id = b.employee_id
        WHERE DATE_FORMAT(b.upcoming_birthday, '%m-%d') BETWEEN 
              DATE_FORMAT(CURDATE(), '%m-%d') AND DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL %s DAY), '%m-%d')
    """
    return query_db(query, (days,))

@app.get("/leave/employee/{employee_id}")
def get_leave_records(employee_id: int):
    query = "SELECT * FROM leaves WHERE employee_id = %s"
    return query_db(query, (employee_id,))

@app.get("/employees/department")
def get_employees_by_department(department: str):
    query = "SELECT * FROM employees WHERE department = %s"
    return query_db(query, (department,))

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

