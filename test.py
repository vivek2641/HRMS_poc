import requests

url = "http://127.0.0.1:8000/birthdays/upcoming"
response = requests.get(url)

# Print the HTTP status code and response content
print("Status Code:", response.status_code)
print("Response JSON:", response.json())  # or response.text if it's not JSON
print("Response:", response)
