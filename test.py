from chatbot_openai import get_endpoint_response,summarize_user_query
from main import get_data


while True:
    employee_id = str(input("Employee ID: "))
    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            print("Thank you!")
            break  
        else:
            endpoint_list = get_endpoint_response(user_message)
            print(endpoint_list)
            if endpoint_list == []:
                print("Bot: I'm sorry, I don't understand your query.")
            else:
                data = get_data(employee_id, endpoint_list)
                print(data)
                final_response = summarize_user_query(user_message, data)
                print("Bot:", final_response)
                   
    break
