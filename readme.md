# 🚀 Backend Blog Project (FastAPI)

A backend system for a blogging platform built using **FastAPI**, with structured content management, clean architecture, and database integration.

---

# ⚙️ Tech Stack

- FastAPI — Backend Framework  
- SQLAlchemy — ORM  
- MySQL / PostgreSQL — Database  
- Uvicorn — ASGI Server  
- Pydantic — Data Validation  
- pyodbc — Database Connector  

---

# 📁 Project Structure

```
Backend-Blog-Project/
│
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── database/
│   └── services/
│
├── requirements.txt
├── README.md
└── .env
```

---

# ⚡ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone <repo-link>
cd Backend-Blog-Project
```

## 2️⃣ Create Environment

```bash
conda create -n blog_env python=3.10
conda activate blog_env
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
conda install pyodbc
```

## 4️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

---

# 🌐 API Access

- 🏠 Home: http://127.0.0.1:8000  
- 📘 Swagger UI: http://127.0.0.1:8000/docs  
- 📄 ReDoc: http://127.0.0.1:8000/redoc  

---

# 🧪 Testing Steps

- Open `/docs`
- Test first endpoints
- Check database connection
- Run CRUD operations:
  - Create Post
  - Read Posts
  - Update Post
  - Delete Post
- Monitor terminal logs

---

# ⚠️ Notes

- File name must be: `requirements.txt`
- Always activate environment before running
- Run commands from project root
- If uvicorn fails use: `app.main:app`

---

# 📦 Features

- Blog CRUD system
- Clean modular architecture
- Database integration
- Auto-generated API docs

---

# 👨‍💻 Author

Backend Blog Project — Built with FastAPI

