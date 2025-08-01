# 🚀 Real-Time & Intelligent Stock Market Monitoring Platform

A production-ready, developer-friendly template for building robust FastAPI backends.

---

## 🔧 Features

- **FastAPI** – Python async web API
- **PostgreSQL** – Primary relational database
- **SQLAlchemy 2.0** – ORM with full Pydantic support
- **Alembic** – Database migrations
- **Celery + Redis** – Async task queue system
- **Docker + Docker Compose** – Containerized dev environment
- **Pipenv + requirements.txt** – Dual support for Python dependencies
- **Devcontainer for VS Code** – One-click development setup
- **Modular project structure** – Clean, API-first layout
- **`.env` config loading** – via `pydantic-settings`

---

## 🗂️ Project Structure

```text
.
├── app/
│   ├── api/            # API routes
│   ├── core/           # Config, Celery, constants
│   ├── db/             # SQLAlchemy models, Base, session
│   ├── services/       # Business logic, Celery tasks
│   └── main.py         # App entrypoint
├── alembic/            # Alembic migrations
├── .devcontainer/      # VS Code Dev Container setup
├── docker-compose.yml  # Docker service definitions
├── Dockerfile          # Base Docker image
├── Pipfile             # Python dependencies
├── requirements.txt    # Exported from Pipfile
├── .env                # Environment variables
└── README.md
```

---

## ⚙️ Getting Started

### 1️⃣ Prerequisites

Install the following:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

### 2️⃣ Start with Dev Container (Recommended)

1. **Clone the repo:**

    ```bash
    git clone https://gitlab.com/secncy_management-group/intelligent-stock-market-monitoring-platform-backend
    ```

2. **Open with VS Code**  
   When prompted:  
   👉 “Reopen in Container” → Click it.

The devcontainer will:

- Start PostgreSQL & Redis
- Run FastAPI on port 8000
- Start Celery worker
- Mount your code with live reload

**Visit your API:**

- [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3️⃣ Working with Alembic

**Create a new migration:**

```bash
alembic revision --autogenerate -m "add users table"
```

**Apply migrations:**

```bash
alembic upgrade head
```

---

### 4️⃣ Running Celery Tasks

In your code:

```python
from app.core.celery_app import test_task
test_task.delay(2, 3)
```

Logs will show in the Celery worker terminal.

---

## 📚 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy ORM Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Celery Docs](https://docs.celeryq.dev/en/stable/)
- [FastAPI + Celery Guide](https://testdriven.io/blog/fastapi-celery/)
- [Docker Curriculum](https://docker-curriculum.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
- [VS Code Devcontainers](https://code.visualstudio.com/docs/devcontainers/containers)

---

## ❓ FAQ

**How do I add new models?**

1. Create your model in `app/db/models/`
2. Import it in `base.py`
3. Run:

    ```bash
    alembic revision --autogenerate -m "your change"
    alembic upgrade head
    ```

---

**Where do I add background tasks?**

- Put Celery tasks in `app/services/tasks.py` or wherever makes sense.
- Register them in `celery_app.py`.

---

**What if ports are already in use?**

- Edit `docker-compose.yml` and change:

    ```yaml
    ports:
      - "8001:8000"  # example: run FastAPI on 8001 instead of 8000
    ```

---

**How do I restart services?**

From inside the devcontainer terminal:

```bash
docker-compose down
docker-compose up --build
```

Or simply reopen the container.

---

## 🧼 Developer Tips

- Use `black`, `isort`, and `pytest` for clean code
- All settings are configured via `.env` and loaded using `pydantic-settings`
- Logs for Celery show in the terminal that launched it
- Use `alembic history` to track migration state

---

## ✅ Summary

With this template, you can:

- Write clean async APIs with FastAPI
- Store data in Postgres using SQLAlchemy ORM
- Run background jobs with Celery + Redis
- Manage DB schema using Alembic
- Work in a fully containerized