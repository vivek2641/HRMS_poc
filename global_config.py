import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE")