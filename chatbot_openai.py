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

Available endpoints:
1. /employees - Get all employees
2. /employee/ - Get specific employee by ID
3. /birthdays/this-month - Get employees with birthdays this month
4. /birthdays/upcoming - Get upcoming birthdays (default: next 7 days, customizable)
5. /leave/employee/ - Get leave records for an employee
6. /employees/department - Get employees by department
7. /leave/today - Get employees on leave today
8. /employees/status-count - Get count of active/inactive employees
9. /employees/recent-joiners - Get employees hired in last 30 days
10. /leave/no-leave-this-year - Get employees who haven't taken leave this year
11. /leave-balances/ - Get leave balance for an employee

Instructions:
- Identify **all** endpoints that match the user's query based on keywords.
- Respond with a list of endpoints.
- Do NOT include explanation, reasoning, or any extra text.
- Ensure each matching endpoint is present only once.

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
- Read the user's query and the provided employee data.
- Respond in a formal, grammatically correct sentence.
- Do not return JSON.
- Do not explain your reasoning.
- Use the employee's full name in the response.
- Include leave types like Casual, Sick, Unpaid, Adjustment in the output.

User Query:
{user_query}

Data:
{data}

Provide a natural language response based only on the above data.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

## testing function
# user = "leave balance"
# data = [{'first_name': 'James', 'last_name': 'Wilson', 'Casual': 2, 'Sick': 5, 'Unpaid': 5, 'Adjustment': 7, 'total': 19}]

# print("summarize_user_query",summarize_user_query(user, data)) 
# print("get_endpoint_response",get_endpoint_response(user))