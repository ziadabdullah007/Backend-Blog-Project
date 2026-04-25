# 📌 Backend Blog Project

A backend system for a blogging platform with structured content management built using FastAPI.

---

# ⚙️ Tech Stack

- FastAPI (Backend Framework)
- SQLAlchemy (ORM)
- MySQL / PostgreSQL (Database)
- Uvicorn (ASGI Server)
- Pydantic (Data Validation)
- pyodbc (Database Connector)

---

# 🚀 Full Setup & Run Guide

## 1️⃣ Clone the Project

git clone <repo-link>  
cd Backend-Blog-Project  

---

## 2️⃣ Create Virtual Environment

conda create -n blog_env python=3.10  
conda activate blog_env  

---

## 3️⃣ Install Requirements

pip install -r requierments.txt

---

## 4️⃣ Install Database Driver (if needed)

conda install pyodbc  

---

## 5️⃣ Run the Project

uvicorn app.main:app --reload  

---

# 🌐 Open in Browser after run prev command 

Home:  
http://127.0.0.1:8000  

Swagger UI:  
http://127.0.0.1:8000/docs  

ReDoc:  
http://127.0.0.1:8000/redoc  

---

# 📁 Project Structure

├── main.py  
├── database/
├── routes/  
├── database/  
├── schemas/  
└── utils/  

---

# 🧪 Testing Steps

- Open `/docs`
- Test first 4 endpoints
- Check database connection
- Run CRUD operations:
  - Create Post
  - Read Posts
  - Update Post
  - Delete Post
- Monitor terminal logs

---

# ⚠️ Notes

- File name must be: requierments.txt
- Always activate environment before running  
- Run commands from project root  
- If uvicorn fails use: app.main:app  

---

# 📦 Features

- Blog CRUD system
- Clean modular architecture
- Database integration
- Auto-generated API docs

---

# 👨‍💻 Author

Backend Blog Project — Built with FastAPI
