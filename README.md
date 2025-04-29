# HRMS POC – FastAPI Application

This is a proof-of-concept (POC) HRMS (Human Resource Management System) backend built with **FastAPI**.

## 🚀 Features

- Employee birthdate and leave analytics
- RESTful API built with FastAPI
- Lightweight and easy to extend

---

## 🧱 Requirements

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

---

## 📦 Setup Instructions

### 1. Clone the Repository, set up env, install requirements and run fastAPI

```bash
git clone https://github.com/your-username/hrms-poc.git
cd hrms-poc

python3 -m venv hrms_poc_venv
source hrms_poc_venv/bin/activate  # Linux/macOS
# hrms_poc_venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
