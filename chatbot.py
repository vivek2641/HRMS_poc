from fastapi import HTTPException
from global_config import OPENAI_API_KEY
import mysql.connector
from global_config import MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, MYSQL_USER
from datetime import datetime
import openai

class ChatBot:
    def init(self):
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = """
        You are a helpful HR assistant for a company. Your role is to assist employees with their HR-related questions.
        Be polite, professional, and concise in your responses. If you don't know an answer, direct the employee to
        contact the HR department directly.
        """
    def get_db_connection(self):
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

    def get_chat_history(self, employee_id: int, limit: int = 10):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM chat_history 
            WHERE employee_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        cursor.execute(query, (employee_id, limit))
        results = cursor.fetchall()
        conn.close()
        return results

    def save_message(self, employee_id: int, message: str, is_bot: bool):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO chat_history 
            (employee_id, message, is_bot, timestamp) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (employee_id, message, is_bot, datetime.now()))
        conn.commit()
        conn.close()

    def generate_response(self, employee_id: int, user_message: str):
        # Get recent chat history for context
        history = self.get_chat_history(employee_id)
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add history to messages (in chronological order)
        for msg in reversed(history):
            role = "assistant" if msg['is_bot'] else "user"
            messages.append({"role": role, "content": msg['message']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            bot_response = response.choices[0].message.content
            
            # Save both messages to history
            self.save_message(employee_id, user_message, False)
            self.save_message(employee_id, bot_response, True)
            
            return bot_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))