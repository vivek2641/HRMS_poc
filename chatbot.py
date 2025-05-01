# from langchain_groq import ChatGroq
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
# from dotenv import load_dotenv
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate

# load_dotenv()

# import os

# # Set Groq API Key
# GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# # Define the prompt template with conversation history
# prompt_template = PromptTemplate(
#     input_variables=["human_input"],
#     template="""
# You are an AI assistant for HRMS. 
# Your job is to analyze the user's query and determine which API endpoints would provide the requested information.

# Available endpoints:
# 1. /employees - Get all employees
# 2. /employee/ - Get specific employee by ID
# 3. /birthdays/this-month - Get employees with birthdays this month
# 4. /birthdays/upcoming - Get upcoming birthdays (default: next 7 days, customizable)
# 5. /leave/employee/ - Get leave records for an employee
# 6. /employees/department - Get employees by department
# 7. /leave/today - Get employees on leave today
# 8. /employees/status-count - Get count of active/inactive employees
# 9. /employees/recent-joiners - Get employees hired in last 30 days
# 10. /leave/no-leave-this-year - Get employees who haven't taken leave this year
# 11. /leave-balances/ - Get leave balance for an employee

# Your response should ONLY be a list of endpoint paths that would satisfy the user's query.
# Example responses:
# - For "who's on leave today": ["/leave/today"]
# - For "employees in marketing department": ["/employees/department"]
# - For "show me my leave balance": ["/leave-balances/"]

# Current query: {human_input}
# """
# )

# # Initialize Groq model
# llm = ChatGroq(model_name="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY)

# # Create the LLM Chain
# CHATBOT_CHAIN = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

# # Function to chat with the model and maintain session in Redis
# def chat_with_model(user_input):
#     """Processes user input, retrieves session history, gets AI response, and stores both in Redis."""
#     ai_response = CHATBOT_CHAIN.run({"human_input": user_input})
#     return ai_response 
        

# while True:
#     user_message = input("You: ")
#     if user_message.lower() in ["exit", "quit"]:
#         print("thank you")  
#         break
#     response = chat_with_model(user_message)
#     print("Bot:", response)




from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

load_dotenv()

# Set Groq API Key
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Define the prompt template with conversation history
prompt_template = PromptTemplate(
    input_variables=["human_input"],
    template="""
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

Your response should ONLY be a list of endpoint paths that would satisfy the user's query.
Example responses:
- For "who's on leave today": ["/leave/today"]
- For "employees in marketing department": ["/employees/department"]
- For "show me my leave balance": ["/leave-balances/"]

Current query: {human_input}
"""
)

# Initialize Groq model
llm = ChatGroq(model_name="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY)

# Create the LLM Chain
CHATBOT_CHAIN = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

# Dictionary to store conversation history per employee
conversation_history = {}

def chat_with_model(user_input, employee_id):
    """Processes user input, maintains conversation history, and returns AI response."""
    
    # Initialize conversation history for employee if not exists
    if employee_id not in conversation_history:
        conversation_history[employee_id] = []
    
    # Add user message to history
    conversation_history[employee_id].append({
        "role": "user",
        "content": user_input
    })
    
    # Get AI response
    ai_response = CHATBOT_CHAIN.run({"human_input": user_input})
    
    # Add AI response to history
    conversation_history[employee_id].append({
        "role": "assistant",
        "content": ai_response
    })
    
    return ai_response, conversation_history

# #Example usage
# while True:
#     employee_id = str(input("You: "))
#     user_message = input("You: ")
#     if user_message.lower() in ["exit", "quit"]:
#         print("Thank you!")
#         print("Final conversation history:")
#         print(conversation_history)  
#         break
    
#     response, history = chat_with_model(user_message, employee_id)
#     print("Bot:", response)

def chat_summary(user_message: str, data: dict) -> str:
    prompt_template = PromptTemplate(
        input_variables=["user_message", "data"],
        template="""
        You are an AI assistant for HRMS. 
        Analyze the user's query and the provided data to generate a helpful response.
        Generate short but impactful and informative response (stricly follow this instruction)
        
        User query: {user_message}
        Available data: {data}
        
        Provide a clear, concise response using this data.
        """
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    return chain.run({"user_message": user_message, "data": data})


    