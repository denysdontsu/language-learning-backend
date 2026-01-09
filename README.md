# 🌍 Language Learning Platform API (WIP)

Backend API for a language learning platform.

The project is in early development stage and serves as an engineering portfolio.

## 📡 API Endpoints (Implemented)

### Authentication

- **POST** `/auth/register` — Simple user registration
    - Request: `UserCreate` (email, username, name, native_language, password)
    - Response: `UserBrief` (201 Created)
    - Validates email/username uniqueness, password strength

- **POST** `/auth/register/complete` — Registration with learning language
    - Request: `UserCreateWithLanguage` (+ active_learning_language, active_language_level)
    - Response: `UserBriefWithLang` (201 Created)
    - Creates user and language entry in single transaction

**Login:**

- **POST** `/auth/token` — OAuth2 login (for Swagger UI)
    - Request: Form data (username=email, password)
    - Response: `{"access_token": "...", "token_type": "bearer"}`
    - Used by Swagger UI "Authorize" button

- **POST** `/auth/login` — JSON login (for frontend)
    - Request: `UserLogin` (email, password)
    - Response: `{"access_token": "...", "token_type": "bearer"}`
    - Returns JWT token for authentication

### User languages

- **GET** `/users/me/languages` — Get user's learning languages
    - Response: `list[UserLanguageBrief]`
    - Requires active learning language
    - Returns empty list if no languages

- **POST** `/users/me/languages/{language}` — Add or update learning language
    - Path param: `language` (ISO 639-1 code: en, uk, de)
    - Request: `UserLanguageLevelUpdate` (level, make_active)
    - Response: `UserLanguageBrief` (201 Created)
    - Creates if not exists (defaults to A1), updates if exists

**Note:** Authentication required for `/users/me/*` endpoints (JWT Bearer token).

---

## 🛠️ Tech Stack

**Implemented:**

- Python 3.11+
- SQLAlchemy 2.0 (async)
- PostgreSQL 14+
- Pydantic v2
- Alembic (migrations)
- python-jose (JWT)
- argon2-cffi (password hashing)
- Poetry (dependency management)

**Planned:**

- FastAPI 0.118+ (in development)
- pytest (testing)

---

## 🧩 Current Progress

### ✅ Implemented

- **Database layer:**
    - SQLAlchemy 2.0 async models with relationships
    - Alembic migrations (7 revisions)  // ← было 4, стало 7
    - Database constraints (email format, positive time, translation completeness)
    - Optimized indexes (partial, composite, unique)
- **Schema layer:**
    - Pydantic v2 schemas with validation
    - Enums for languages, levels, and exercise types
    - Business logic validation (exercise options, translations)
    - Circular import resolution using TYPE_CHECKING
- **Core utilities:**
    - Application configuration (Pydantic Settings)
    - Async PostgreSQL connection
    - Security utilities (JWT, password hashing, Argon2)
    - Dependency injection with FastAPI
    - JWT authentication with role-based access
- **CRUD layer:**
    - Users: create, read by id/email/username, update active language
    - User languages: create, read, update, get all by user
- **Services layer:**
    - Authentication: user registration (simple & with language), login
    - User languages: add/update learning languages
- **API endpoints:**
    - Authentication: POST /auth/register, /auth/register/complete
    - User languages: GET /users/me/languages, POST /users/me/languages/{language}

### 🟡 In Development

- CRUD layer (exercises, exercise history)
- Services layer (exercises, history, statistics)
- API endpoints (exercises, user profile, history)
- Login endpoint and token refresh

### 🔴 Planned

- User history and statistics
- Admin panel for exercise management
- Unit and integration tests (pytest)
- Docker setup
- CI/CD pipeline
- AI-powered exercise generation (V2)

---

## 🗄️ Data Model

```sql
user
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

user_level_language
├─ id (PK)
├─ user_id (FK → users.id)
├─ language (enum: uk, en, de)
├─ level (enum: A1, A2, B1, B2, C1, C2)
├─ created_at
└─ [UNIQUE INDEX] (user_id, language)

exercise
├─ id (PK)
├─ topic
├─ difficult_level (enum: A1-C2)
├─ type (enum: sentence_translation, multiple_choice, fill_blank)
├─ question_text
├─ question_language (enum: uk, en, de)
├─ correct_answer
├─ answer_language (enum: uk, en, de)
├─ options (JSONB, nullable)
├─ question_translation (nullable | str)
├─ question_translation_language (nullable | enum: uk, en, de)
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
    5. Add unique constraint and make active_learning_language nullable
    6. Remove duplicate unique index on user_level_languages
    7. Add ' fill_blank' to exercise type enum

---

## 🏗️ Project Architecture

```sql
app/
├── core/
│   ├── config.py             # Pydantic Settings
│   └── security.py           # JWT & Argon2 
│
├── db/
│   ├── __init__.py
│   ├── column_types.py       # Custom SQLAlchemy types
│   └── connection.py         # Async SQLAlchemy engine
│
├── api/                      # Partially implemented
│   ├── endpoints/
│   │   ├── auth.py           # Registration endpoints
│   │   └── languages.py      # Language management endpoints
│   └── dependencies.py       # Dependency injection
│
├── crud/                     # Partially implemented
│   ├── user.py               # User CRUD operations
│   ├── user_language.py      # Language CRUD operations
│   ├── exercise.py           # 🟡 In development
│   └── exercise_history.py   # 🟡 In development
│
├── services/                 # Partially implemented
│   ├── __init__.py
│   ├── auth.py               # Registration & authentication
│   └── user_language.py      # Language management logic
│
├── models/                   # SQLAlchemy models
│   ├── user.py
│   ├── user_level_language.py
│   ├── exercise.py
│   └── user_exercise_history.py
│
├── schemas/                  # Pydantic schemas & Enums
│   ├── common.py             # Options
│   ├── enums.py              # Language, Level, ExerciseType
│   ├── token.py              # JWT token schemas
│   ├── user.py
│   ├── user_level_language.py
│   ├── exercise.py
│   └── user_exercise_history.py
│
├── utils/                    
│   ├── validators.py         # Business logic validation
│   └── enum_utils.py         # Enum helpers
│
└── main.py                   # FastAPI app

migrations/                   # Alembic migrations
├── versions/
│   ├── 99a19fb9275f_initial.py
│   ├── f47b1a71c0df_add_translation_completeness_check.py
│   ├── f4962d68824f_add_active_learning_language_reference.py
│   ├── 3ebb198c91e4_add_non_nullable_text_column.py
│   ├── f363429e20bf_add_unique_constraint_and_make_active_.py
│   ├── 808ed363444b_remove_duplicate_unique_index_on_user_.py
│   └── e9d426e6d045_add_fill_blank_to_exercise_type_enum.py
├── env.py
└── script.py.mako
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

**Generate a secure SECRET_KEY:**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
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

### 6. Run the application

Start the FastAPI development server:
```bash
poetry run uvicorn app.main:app --reload
```

**Access the API:**
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

Use Swagger UI to test endpoints interactively.
⚠️ API is partially implemented and subject to change.

---

## 🗺️ Roadmap

### Phase 1: Backend Core (current stage)

- [x]  Database schema design
- [x]  SQLAlchemy models + relationships
- [x]  Alembic migrations
- [x]  Pydantic schemas
- [x]  Database constraints & indexes
- [x]  JWT authentication & dependencies
- [x]  CRUD operations (users, languages)
- [x]  User registration endpoints (simple & with language)
- [x]  Login endpoint (OAuth2 + JSON)

### Phase 2: API & Features

- [ ]  User profile management
- [ ]  Languages endpoint
- [ ]  Exercise CRUD
- [ ]  Exercise submission & validation
- [ ]  Exercise endpoint
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