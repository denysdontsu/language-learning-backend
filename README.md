# 🌍 Language Learning Platform API (WIP)

Backend API for a language learning platform.

The project is in early development stage and serves as an engineering portfolio.

> ⚠️ Status: Early development (V0.1)
>
>
> SQLAlchemy models, Pydantic schemas, and core utilities are implemented.
>
> API and business logic are under development.
>

---

## 🛠️ Tech Stack

**Implemented:**

- Python 3.11+
- SQLAlchemy 2.0 (async)
- PostgreSQL 14+
- Pydantic v2
- Alembic (migrations)
- Poetry (dependency management)

**Planned:**

- FastAPI 0.118+ (in development)
- python-jose (JWT)
- passlib[bcrypt] (password hashing)
- pytest (testing)

---

## 🧩 Current Progress

### ✅ Implemented

- **Database layer:**
    - SQLAlchemy 2.0 async models with relationships
    - Alembic migrations (4 revisions)
    - Database constraints (email format, positive time, translation completeness)
    - Optimized indexes (partial, composite, unique)
- **Schema layer:**
    - Pydantic v2 schemas with validation
    - Enums for languages, levels, and exercise types
    - Business logic validation (exercise options, translations)
- **Core utilities:**
    - Application configuration (Pydantic Settings)
    - Async PostgreSQL connection

### 🟡 In Development

- Security utilities (JWT, password hashing)
- CRUD layer (users, exercises, user_languages, history)
- JWT authentication
- API endpoints (FastAPI)
- Dependency injection (get_db, get_current_user)

### 🔴 Planned

- User history and statistics
- Admin panel for exercise management
- Unit and integration tests
- Docker setup
- CI/CD pipeline
- AI-powered exercise generation (V2)

---

## 🗄️ Data Model

```sql
users
├─ id (PK)
├─ email (UNIQUE, CHECK: valid format)
├─ username (UNIQUE)
├─ name
├─ hashed_password
├─ native_language (enum: uk, en, de)
├─ active_learning_language_id (FK → user_level_languages.id)
├─ role (default: 'user')
├─ is_active (default: true)
└─ created_at

user_level_languages
├─ id (PK)
├─ user_id (FK → users.id)
├─ language (enum: uk, en, de)
├─ level (enum: A1, A2, B1, B2, C1, C2)
├─ created_at
└─ [UNIQUE INDEX] (user_id, language)

exercises
├─ id (PK)
├─ topic
├─ difficult_level (enum: A1-C2)
├─ type (enum: sentence_translation, multiple_choice, fill_blank)
├─ question_text
├─ question_language (enum: uk, en, de)
├─ correct_answer
├─ answer_language (enum: uk, en, de)
├─ options (JSONB, nullable)
├─ question_translation (nullable)
├─ question_translation_language (nullable)
├─ is_active (default: true)
├─ added_at
├─ [CHECK] translation completeness
└─ [PARTIAL INDEX] (topic, difficult_level) WHERE is_active=true

user_exercise_history
├─ id (PK)
├─ user_id (FK → users.id)
├─ exercise_id (FK → exercises.id)
├─ user_answer
├─ is_correct
├─ time_spent_seconds (CHECK: > 0)
├─ completed_at
├─ [INDEX] (user_id, completed_at)
└─ [INDEX] (user_id, exercise_id)
```

**Enums:**

- **LanguageEnum:** uk (Ukrainian), en (English), de (German)
- **LanguageLevelEnum:** A1, A2, B1, B2, C1, C2 (CEFR standard)
- **ExerciseTypeEnum:** sentence_translation, multiple_choice, fill_blank

---

## 🗃️ Database Implementation Features

### Database-level validation

- **check_email_format** — email validation at PostgreSQL level
- **positive_time** — ensures positive exercise completion time
- **check_translation_complete** — both translation fields are filled together or both NULL

### Performance optimizations

- **Partial index** on active exercises (`topic`, `difficult_level`)
    - Speeds up filtering when fetching exercises
    - Saves space (inactive exercises not indexed)
- **Composite indexes** for statistics
    - `(user_id, completed_at)` — history by time
    - `(user_id, exercise_id)` — JOINs for analytics
- **Unique index** on `(user_id, language)`
    - Prevents duplicate languages per user
    - Speeds up lookups

### Migrations

- 4 Alembic revisions:
    1. Initial schema (users, exercises, relationships)
    2. Add constraints (translation completeness)
    3. Add active learning language reference to user and rename translation fields
    4. Add non-nullable text column to persist user answers for exercises

---

## 🏗️ Project Architecture

```sql
app/
├── core/
│   ├── config.py             # Pydantic Settings
│   └── security.py           # 🟡 In development
│
├── db/
│   ├── __init__.py
│   ├── column_types.py       # Custom SQLAlchemy types
│   └── connection.py         # Async SQLAlchemy engine
│
├── api/                      # 🟡 In development
│   ├── endpoints/
│   └── dependencies.py
│
├── crud/                     # 🟡 In development
│   ├── user.py
│   ├── user_language.py
│   ├── exercise.py
│   └── exercise_history.py
│
├── models/                   # ✅ Implemented
│   ├── users.py
│   ├── user_level_languages.py
│   ├── exercises.py
│   └── user_exercise_history.py
│
├── schemas/                  # ✅ Implemented
│   ├── common.py             # Options
│   ├── enums.py              # Language, Level, ExerciseType
│   ├── user.py
│   ├── user_level_language.py
│   ├── exercise.py
│   └── user_exercise_history.py
│
├── utils/                    # ✅ Implemented
│   ├── validators.py         # Business logic validation
│   └── enum_utils.py         # Enum helpers
│
└── main.py                   # FastAPI app (stub)

migrations/                   # ✅ Implemented
├── versions/
│   ├── 99a19fb9275f_initial.py
│   ├── 3ebb198c91e4_add_non_nullable_text_column.py
│   ├── f47b1a71c0df_add_translation_completeness_check.py
│   └── f4962d68824f_add_active_learning_language_reference.py
└── env.py

.env.example                  # Configuration example
alembic.ini                   # Alembic configuration
pyproject.toml                # Project configuration and dependencies.
poetry.toml                   # Locked dependency versions.
README.md
```

**Principles:**

- Clear layer separation (models, schemas, crud, api)
- Async-first approach (AsyncSession, async def)
- Three-level validation:
    1. Pydantic (request/response)
    2. Business logic (validators.py)
    3. Database (constraints)

---

## 🚀 Quick Start (for developers)

### 1. Clone the repository
```bash
git clone https://github.com/denisdoncu/LanguageProject.git
cd LanguageProject
```

### 2. Install dependencies

Poetry manages virtual environments automatically:
```bash
poetry install
```

**First time using Poetry?** Install it:
```bash
# Install poetry
pip install poetry

# Verify installation
poetry --version
```

### 3. Configure .env
```bash
cp .env.example .env
```

Fill in `.env`:
```env
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres_db_name
SECRET_KEY=your-secret-key-min-32-chars
```

### 4. Create database
```bash
# PostgreSQL
createdb language_db

# Or via psql
psql -U postgres
CREATE DATABASE language_db;
\q
```

### 5. Apply migrations
```bash
poetry run alembic upgrade head
```

**Note:** `poetry run` ensures commands execute in Poetry's virtual environment.

### 6. Current state

⚠️ **API endpoints are not implemented.**

Only the database layer (models + migrations) is available.

To view database structure:
```bash
psql -d language_db -c "\dt"       # List tables
psql -d language_db -c "\d users"  # users table structure
```

---

## 🚧 Current Version Limitations

- ❌ No API endpoints
- ❌ No authentication
- ❌ No business logic (CRUD)
- ❌ No tests
- ❌ Not intended for production

The project is at the architecture design and data layer stage.

---

## 🗺️ Roadmap

### Phase 1: Backend Core (current stage)

- [x]  Database schema design
- [x]  SQLAlchemy models + relationships
- [x]  Alembic migrations
- [x]  Pydantic schemas
- [x]  Database constraints & indexes
- [ ]  CRUD operations
- [ ]  JWT authentication
- [ ]  API endpoints

### Phase 2: API & Features

- [ ]  User registration & login
- [ ]  User profile management
- [ ]  Language management (add, update, remove)
- [ ]  Exercise CRUD
- [ ]  Exercise submission & validation
- [ ]  History tracking
- [ ]  Statistics calculation

### Phase 3: Admin & Polish

- [ ]  Admin panel
- [ ]  Filtering & pagination
- [ ]  Unit tests
- [ ]  Integration tests
- [ ]  Docker setup
- [ ]  CI/CD

### Phase 4: Advanced (V2)

- [ ]  AI-powered exercise generation
- [ ]  Refresh Token
- [ ]  Email verification
- [ ]  Password recovery

---

## 👤 Author

**Denys Dontsu**

GitHub: [@denysdontsu](https://github.com/denysdontsu)

Project created for learning FastAPI, SQLAlchemy 2.0 (async), and REST API design.

---

![Status](https://img.shields.io/badge/status-early%20development-yellow)

![Python](https://img.shields.io/badge/python-3.11+-blue)

![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0-green)

![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue)

**Version:** 0.1.0-alpha

**Last updated:** December 2025