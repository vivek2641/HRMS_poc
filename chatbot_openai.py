import os
import ast
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client with your OpenAI key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"



def get_endpoint_response(query):
    PROMPT_TEMPLATE = """
You are an AI assistant for HRMS. 
Your job is to analyze the user's query and determine which API endpoints would provide the requested information.

Table details:
1. employees
    Description: Stores all employee information.
    Columns:employee_id (PK), first_name, last_name, email (unique),phone,department,position,hire_date,salary,manager_id (FK to employee_id in employees),is_active

2. birthdays
    Description: Stores employee birth dates.
    Columns:birthday_id (PK),employee_id (FK to employees),birth_date

3. leaves
    Description: Stores employee leave records.
    Columns:leave_id (PK),employee_id (FK to employees),leave_type (enum),start_date,end_date,status (enum),reason,applied_date,approved_by (FK to employees)
    Constraints: end_date ≥ start_date

4. leave_balance
    Description: Stores leave balance for each employee.
    Columns:employee_id (PK, FK to employees),Casual,Sick,Unpaid,Adjustment,total (generated as sum of leave types)


Available endpoints:
1. Endpoint: /employees
    Description: Fetches all employee records.
    Table: employees
    Columns: employee_id, first_name, last_name, email, phone, department, position, hire_date, salary, manager_id, is_active
    Query: SELECT * FROM employees

2. Endpoint: /employee/
    Description: Retrieves detailed info for a specific employee by employee_id, including personal, birthday, leave, and leave balance data.
    Tables & Columns:
    employees: all columns
    birthdays: all columns
    leaves: all columns
    leave_balance: all columns
    Query: Joins employees with birthdays, leaves, and leave_balance using employee_id, filtered by the given employee_id.

3.Endpoint: /birthdays/this-month
    Description: Fetches details of employees whose birthdays fall in the current month.
    Tables & Columns:
    employees: all columns
    birthdays: birth_date
    Query: Joins employees and birthdays on employee_id, filters by current month using MONTH(birth_date) = MONTH(CURDATE()).
    
4. Endpoint: /birthdays/upcoming
    Description: Retrieves employees with birthdays within the next specified number of days (default is 7).
    Tables & Columns:
    employees: all columns
    birthdays: birth_date
    Query: Joins employees and birthdays on employee_id, filters using DATE_FORMAT to match upcoming MM-DD values, and orders the result chronologically.
        
5. Endpoint: /leave/employee/
    Description: Retrieves all leave records for a specific employee by employee_id.
    Table: leaves
    Columns: all columns
    Query: SELECTs from leaves table where employee_id matches the given ID.


6. Endpoint: /employees/department/
    Description: Retrieves basic employee details (ID, name, department) for a specific employee.
    Table: employees
    Columns: employee_id, first_name, last_name, department
    Query: SELECTs specific columns from employees table where employee_id matches the given ID.

7. Endpoint: /leave/today
    Description: Retrieves details of employees who are currently on leave today.
    Tables & Columns:
    employees: all columns
    leaves: start_date, end_date
    Query: Joins employees and leaves on employee_id; filters records where today’s date falls within the leave period.

8. Endpoint: /employees/status-count
    Description: Returns the count of employees grouped by their active status (active/inactive).
    Table: employees
    Columns: is_active
    Query: SELECTs is_active and counts grouped by is_active from the employees table.

9. Endpoint: /employees/recent-joiners
    Description: Retrieves employees who joined in the last 30 days.
    Table: employees
    Columns: all columns
    Query: SELECTs all records from employees where hire_date is within the last 30 days.

10. Endpoint: /leave/no-leave-this-year
    Description: Retrieves employees who haven't taken any leave in the current year.
    Tables & Columns:
    employees: all columns
    leaves: employee_id, start_date
    Query: SELECTs all employees whose employee_id is not in the list of those who have leave records with a start_date in the current year.

11. Endpoint: /leave-balances/
    Description: Retrieves the leave balance details for a specific employee, including name and leave types.
    Tables & Columns:
    leave_balance: Casual, Sick, Unpaid, Adjustment, total
    employees: first_name, last_name
    Query: Joins leave_balance with employees on employee_id and filters by the given employee_id. Raises 404 if no record found.

Instructions:
- Identify all endpoints that match the user's query based on keywords.
- Respond with a list of endpoints.
- Do NOT include explanation, reasoning, or any extra text.
- Ensure each matching endpoint is present only once.
- If user need there own details than you can return the /employee/ endpoint
- If need for all the depoyee details than you acn use /employees only 

Example responses:
- "who's on leave today": ["/leave/today"]
- "employees in marketing department": ["/employees/department"]
- "show me my leave balance": ["/leave-balances/"]
- "birthday of employee 113": ["/employee/", "/birthdays/this-month"]

Current query: {human_input}
"""

    try:
        formatted_prompt = PROMPT_TEMPLATE.format(human_input=query)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        return ast.literal_eval(content)  # Safely convert to list
    except Exception as e:
        return f"Error: {str(e)}"

def summarize_user_query(user_query: str, data: list[dict]) -> str:
    """Generate a natural language summary of leave balances based on the user's query and data."""
    prompt = f"""
You are an AI assistant for an HRMS system.

Instructions:
- The data provided is directly fetched from the database using a query, and is accurate. Your task is only to rephrase this data into a plain, human-readable response. Do not modify, filter, or exclude any entries.- Read the user's query and give Response.
- Respond in a formal, grammatically correct sentence.
- Do not return JSON.
- Do not explain your reasoning.
- Use the employee's full name in the response.
- Include leave types like Casual, Sick, Unpaid, Adjustment in the output.
- If you found upcoming and birhday and any numarical number than take as upcoming days number and return all name of the data you got.
- first check the user query and use the data for generate the answer. Quertions may depended on all data or signle data.
- You must read all the data and respond according to the user's question. Identify relevant information from the data and return answers based on the user's query.

User Query:
{user_query}
\n\n
Data:
{data}
\n\n
Provide a natural language response based only on the above data.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

## testing function
# user = "leave balance"
# data = [{'first_name': 'James', 'last_name': 'Wilson', 'Casual': 2, 'Sick': 5, 'Unpaid': 5, 'Adjustment': 7, 'total': 19}]

# print("summarize_user_query",summarize_user_query(user, data)) 
# print("get_endpoint_response",get_endpoint_response(user))