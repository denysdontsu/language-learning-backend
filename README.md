# 🌍 Language Learning Platform API

Backend REST API for an interactive language learning platform with spaced repetition and progress tracking.

The project is in early development stage.

## 📡 API Endpoints

Full details available in Swagger UI at `/docs`.

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Simple user registration | — |
| POST | `/auth/register/complete` | Registration with learning language | — |
|--------|----------|-------------|------|
| POST | `/auth/token` | OAuth2 login (Swagger UI) | — |
| POST | `/auth/login` | JSON login (frontend) | — |

### User Management
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me/` | Get current user profile | ✓ |
| POST | `/users/me/` | Update user profile | ✓ |
| PATCH | `/users/me/password` | Change password | ✓ |
|--------|----------|-------------|------|
| GET | `/users/me/languages` | Get learning languages | ✓ |
| POST | `/users/me/languages/{language}` | Add or update language | ✓ |
| DELETE | `/users/me/languages/{language}` | Remove language | ✓ |

### Exercises
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/exercises/topics` | Get available topics | ✓ |
| GET | `/exercises/next` | Get next exercise | ✓ |
| POST | `/exercises/{id}/submit` | Submit answer | ✓ |

### History & Statistics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/history/` | Exercise history with filters | ✓ |
| GET | `/history/{id}` | History record detail | ✓ |
|--------|----------|-------------|------|
| GET | `/users/me/statistics/` | Overview metrics | ✓ |
| GET | `/users/me/statistics/performance` | Performance analysis | ✓ |

### Admin
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/users/` | Get users list with filters | ✓ Admin |
| GET | `/admin/users/{user_id}` | Get user details | ✓ Admin |
| PATCH | `/admin/users/{user_id}` | Update user | ✓ Admin |
|--------|----------|-------------|------|
| POST | `/admin/exercises/` | Create exercise | ✓ Admin |
| GET | `/admin/exercises/` | Get exercises list with filters | ✓ Admin |
| GET | `/admin/exercises/{exercise_id}` | Get exercise details with stats | ✓ Admin |
| PATCH | `/admin/exercises/{exercise_id}` | Update exercise | ✓ Admin |
|--------|----------|-------------|------|
| GET | `/admin/users/{user_id}/languages/` | Get user languages | ✓ Admin |
| POST | `/admin/users/{user_id}/languages/{language}` | Add or update user language | ✓ Admin |
| DELETE | `/admin/users/{user_id}/languages/{language}` | Remove user language | ✓ Admin |
|--------|----------|-------------|------|
| GET | `/admin/statistics/` | Platform-wide statistics | ✓ Admin |
| GET | `/admin/statistics/{user_id}` | Complete user statistics | ✓ Admin |
---

## 🛠️ Tech Stack

**Core:**
- Python 3.11+
- FastAPI 0.118+
- SQLAlchemy 2.0 (async)
- PostgreSQL 17 - 17.10 # ось тут також змінив з 14+, так наче більш точно
- Pydantic v2

**Infrastructure:**
- Alembic (database migrations)
- python-jose (JWT tokens)
- argon2-cffi (password hashing)
- Poetry (dependency management)
- Docker & Docker Compose # додав

**Planned:**
- pytest (unit & integration testing)
- CI/CD pipeline

---

### ✅ Implemented

- **Database:** async SQLAlchemy models, 13 Alembic migrations, DB-level constraints and optimized indexes
- **Schemas:** Pydantic v2 with validation, enums, business logic validation
- **Utilities:** JWT & Argon2 security, dependency injection, date range parsing, normalizers
- **CRUD & Services:** full layered implementation for users, languages, exercises, history, statistics
- **API:** 20 endpoints across auth, users, exercises, history, statistics and admin panel
- **Infrastructure:** Docker & Docker Compose with automated migrations and seed data

### 🟡 In Development

- Unit and integration tests (pytest)

### 🔴 Planned

- CI/CD pipeline
- AI-powered exercise generation (V2)
- Refresh token (V2)
- Email verification & password recovery (V2)

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
├─ role (enum: default: 'user', 'admin')
├─ is_active (default: true)
└─ created_at (timestamp, default: now())

user_level_language
├─ id (PK)
├─ user_id (FK → users.id, CASCADE)
├─ language (enum: uk, en, de)
├─ level (enum: A1, A2, B1, B2, C1, C2)
├─ created_at (timestamp, default: now())
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
├─ explanation (nullable | text)
├─ question_translation (nullable | text)
├─ question_translation_language (nullable | enum: uk, en, de)
├─ is_active (default: true)
├─ added_at (timestamp, default: now())
├─ [CHECK] translation completeness
└─ [PARTIAL INDEX] (topic, difficult_level) WHERE is_active=true

user_exercise_history
├─ id (PK)
├─ user_id (FK → users.id, CASCADE)
├─ exercise_id (FK → exercises.id, RESTRICT)
├─ user_answer
├─ status (enum: correct, incorrect, skip)
├─ time_spent_seconds (CHECK: > 0)
├─ completed_at (timestamp, default: now())
├─ [CHECK] check_status
├─ [INDEX] (user_id, completed_at)
└─ [INDEX] (user_id, exercise_id)
```

**Enums:**

- **LanguageEnum:** uk (Ukrainian), en (English), de (German)
- **LanguageLevelEnum:** A1, A2, B1, B2, C1, C2 (CEFR standard)
- **ExerciseTypeEnum:** sentence_translation, multiple_choice, fill_blank
- **ExerciseStatusEnum:** correct (14-day timeout), skip (3-day timeout), incorrect (no timeout)
- **UserRoleEnum:**  admin, user

---

## Database Implementation Features

### Database-level validation

- **check_email_format** - email validation at PostgreSQL level
- **positive_time** - ensures positive exercise completion time
- **check_translation_complete** - both translation fields are filled together or both NULL

### Performance optimizations

- **Partial index** on active exercises (`topic`, `difficult_level`)
    - Speeds up filtering when fetching exercises
    - Saves space (inactive exercises not indexed)
- **Composite indexes** for statistics
    - `(user_id, completed_at)` - history by time
    - `(user_id, exercise_id)` - JOINs for analytics
- **Unique index** on `(user_id, language)`
    - Prevents duplicate languages per user
    - Speeds up lookups

---

## 🏗️ Project Architecture

```sql
app/
├── core/
│   ├── config.py                    # Pydantic Settings
│   └── security.py                  # JWT & Argon2 
│
├── db/
│   ├── __init__.py
│   ├── column_types.py              # Custom SQLAlchemy types
│   └── connection.py                # Async SQLAlchemy engine
│
├── api/
│   ├── endpoints/
│   │   ├── admin/
│   │   │   ├── __init__.py          # Admin router registration
│   │   │   ├── users.py             # Admin user management
│   │   │   ├── exercises.py         # Admin exercise management
│   │   │   ├── languages.py         # Admin language management
│   │   │   └── statistics.py        # Admin statistics
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── exercises.py             # Exercise practice endpoints
│   │   ├── users.py                 # User management endpoints
│   │   ├── languages.py             # Language management endpoints
│   │   ├── statistics.py            # User learning statistics endpoints
│   │   └── user_exercise_history.py # User exercise history endpoints
│   └── dependencies.py              # Dependency injection
│
├── crud/
│   ├── admin/
│   │   ├── user.py                  # Admin user queries
│   │   ├── exercises.py             # Admin exercise queries
│   │   └── statistics.py            # Admin statistics queries
│   ├── user.py
│   ├── user_language.py
│   ├── exercise.py
│   └── user_exercise_history.py 
│
├── services/                        # Partially implemented
│   ├── admin/
│   │   ├── user.py                  # Admin user logic
│   │   ├── exercises.py             # Admin exercise logic
│   │   └── statistics.py            # Admin logic
│   ├── auth.py                      # Registration & authentication
│   ├── exercise.py                  # Exercise logic with validation
│   ├── statistics.py                # Statistics calculation and aggregation logic
│   ├── user.py                      # User management logic
│   ├── user_exercise_history.py     # User exercise history logic
│   └── user_language.py             # Language management logic
│
├── models/                          # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── user_level_language.py
│   ├── exercise.py
│   └── user_exercise_history.py
│
├── schemas/                         # Pydantic schemas & Enums
│   ├── __init__.py
│   ├── common.py                    # Shared schemas
│   ├── enums.py                     # Application enums
│   ├── jwt_token.py                 # JWT token schemas
│   ├── user.py
│   ├── user_level_language.py
│   ├── exercise.py
│   ├── user_exercise_history.py
│   └── statistics.py
│
├── utils/                    
│   ├── validators.py               # Business logic validation
│   ├── normalizers.py              # Data normalization utilities 
│   ├── helpers.py                  # Stateless helper functions
│   └── enum_utils.py               # Enum helpers
│
└── main.py                         # FastAPI app

migrations/                         # Alembic migrations
├── versions/
│   ├── 99a19fb9275f_initial.py
│   ├── f47b1a71c0df_add_translation_completeness_check.py
│   ├── f4962d68824f_add_active_learning_language_reference.py
│   ├── 3ebb198c91e4_add_non_nullable_text_column.py
│   ├── f363429e20bf_add_unique_constraint_and_make_active_.py
│   ├── 808ed363444b_remove_duplicate_unique_index_on_user_.py
│   ├── e9d426e6d045_add_fill_blank_to_exercise_type_enum.py
│   ├── 860522b56861_fix_foreign_key_user_fk_cascade_.py
│   ├── 756af3813bf4_add_status_column_with_check_constraint.py
│   ├── bf1b5c6bd1d9_remove_is_correct_column.py
│   ├── 9d7c65ea9a7c_add_user_role_enum.py
│   └── b54982218f73_add_explanation_column_to_exercises.py
│
├── env.py
└── script.py.mako

seed.py
Dockerfile
docker-compose.yml
.env.example
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

### Clone the repository
```bash
git clone https://github.com/denysdontsu/language-learning-backend.git
cd language-learning-backend
```

---

### 1. Docker Installation (recommended)

Requires Docker and Docker Compose installed.

**1.1 Configure .env**
```bash
cp .env.example .env
```

Fill in `.env`:
```env
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres_db_name
SECRET_KEY=your-secret-key-min-32-chars
VERSION=0.1.0
```

Note: `POSTGRES_HOST` must be `db` (Docker service name, not `localhost`).

**1.2 Run**
```bash
docker compose up --build
```

On first run automatically:
- Starts PostgreSQL 17
- Applies all migrations
- Seeds the database with sample data
- Starts the API server

**Access the API:**
- Swagger UI: http://localhost:8000/docs

**Seed credentials:**
- Admin: `admin@example.com` / `admin1234`
- User: `alice@example.com` / `alice1234`

---

### 2. Manual Installation

**2.1 Install Poetry (if not installed)**
```bash
pip install poetry

# Verify installation
poetry --version
```

**2.2 Install dependencies**
```bash
poetry install
```

**2.3 Configure .env**
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

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**2.4 Create database**
```bash
createdb postgres_db_name

# Or via psql
psql -U postgres -c "CREATE DATABASE postgres_db_name;"
```

**2.5 Apply migrations**
```bash
poetry run alembic upgrade head
```

**2.6 Run the application**
```bash
poetry run uvicorn app.main:app --reload
```

**Access the API:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
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

### Phase 2: API & Features --- 

- [x]  User profile management
- [x]  Languages endpoint
- [x]  Exercise CRUD
- [x]  Exercise submission & validation
- [x]  Exercise endpoint
- [x]  History tracking
- [x]  Statistics calculation

### Phase 3: Admin & Polish

- [x]  Admin panel
- [ ]  Unit tests
- [ ]  Integration tests
- [x]  Docker setup
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

---

![Status](https://img.shields.io/badge/status-early%20development-yellow)

![Python](https://img.shields.io/badge/python-3.11+-blue)

![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0-green)

![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue)

![Docker](https://img.shields.io/badge/docker-24+-blue)

**Version:** 0.1.0-alpha

**Last updated:** July 2026