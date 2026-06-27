# 🌍 Language Learning Platform API

Backend REST API for an interactive language learning platform with spaced repetition and progress tracking.

The project is in early development stage.

## 📡 API Endpoints (Implemented)

### Authentication

**Registration:**
- **POST** `/auth/register` - Simple user registration
    - Request: `UserCreate` (email, username, name, native_language, password)
    - Response: `UserBrief` (201 Created)
    - Validates email/username uniqueness, password strength

- **POST** `/auth/register/complete` - Registration with learning language
    - Request: `UserCreateWithLanguage` (+ active_learning_language, active_language_level)
    - Response: `UserBriefWithLang` (201 Created)
    - Creates user and language entry in single transaction

**Login:**
- **POST** `/auth/token` - OAuth2 login (for Swagger UI)
    - Request: Form data (`username` = email, password)
    - Response: `{"access_token": "...", "token_type": "bearer"}`
    - Used by Swagger UI "Authorize" button

- **POST** `/auth/login` - JSON login (for frontend)
    - Request: `UserLogin` (email, password)
    - Response: `{"access_token": "...", "token_type": "bearer"}`
    - Returns JWT token for authentication

### User Management

**Authentication required (JWT Bearer token)**

- **GET** `/users/me/` - Get current user profile 
    - Request: JWT Bearer token
    - Response: `UserBriefWithLang` (if active language set) or `UserBrief`
    - Returns user profile with learning progress

- **POST** `users/me` - Update user profile
    - Request: `UserUpdate` (email, username, name, native_language)
    - Response: `UserBrief`
    - Returns updated user profile

- **PATCH** `users/me/password` - Change user password
    - Request: `UserChangePassword` (old_password, new_password)
    - Response: 204 No content
    - Rate limit: 5 requests/hour

### User languages

**Authentication required**

- **GET** `/users/me/languages` - Get learning languages
    - Response: `list[UserLanguageBrief]`
    - Returns all languages user is learning (may be empty)

- **POST** `/users/me/languages/{language}` - Add or update learning language
    - Path param: `language` (ISO 639-1 code: en, uk, de)
    - Request: `UserLanguageLevelUpdate` (level, make_active)
    - Response: `UserLanguageBrief` (201 Created or 200 OK)
    - Creates if not exists (defaults to A1) or update existing 
    - Sets as active if `make_active=True`

- **DELETE** `/users/me/languages/{language}` - Remove learning language
    - Path param: `language` (ISO 639-1 code: en, uk, de)
    - Response: 204 No content
    - Cannot remove language if it's the only language or current active

### Exercise

**Authentication required - Active learning language required**

- **GET** `/exercises/topics` - Get available exercise topics
    - Response: `list[str]`
    - Returns topic for exercises matching user's languages pair (bidirectional)

- **GET** `/exercises/next` - Get next practice exercise
    - Query params:
        - `topic` (required) - Exercise topic
        - `difficult_level` (optional) - CEFR level override (A1-C2), defaults to user's level
        - `exclude_id` (optional) - Exercise ID to skip (prevents immediate repeats)
    - Response: `ExerciseQuestion`
    - Returns random exercise with spaced repetition filtering:
        - Excludes exercises answered correctly in last 14 days
        - Excludes skipped exercises from last 3 days
        - Allows immediate retry of incorrect answers

- **POST** `/exercises/{exercise_id}/submit` - Submit exercise answer
    - Path: `exercise_id` - Exercise to answer
    - Request: `ExerciseUserAnswer` (user_answer, time_spent_seconds)
    - Response: `ExerciseCorrectAnswer` (201 Created)
    - Validates answer (case-insensitive), determines status, saves to history
    - Returns correct answer and optional explanation

### Exercise History

**Authentication required**

- **GET** `/history/` - Get user exercise history
    - Query params:
        - `order` (optional) - Sort order by completion date: `asc` or `desc` (default: `desc`)
        - `language` (optional) - Filter by practiced language (ISO 639-1: en, uk, de)
        - `difficult_level` (optional) - Filter by CEFR level (A1-C2)
        - `status` (optional) - Filter by completion status: `correct`, `incorrect`, `skip`
        - `period` (optional) - Quick time period: `7d`, `30d`, `3m`, `1y`, `all` (overrides custom dates)
        - `date_from` (optional) - Filter from date (YYYY-MM-DD, inclusive)
        - `date_to` (optional) - Filter to date (YYYY-MM-DD, inclusive)
        - `limit` (optional) - Max records to return (from pagination dependency)
        - `offset` (optional) - Records to skip (from pagination dependency)
    - Response: `list[ExerciseHistoryBrief]`
    - Returns paginated exercise history with filtering options
    - Date filtering: use predefined `period` OR custom `date_from`/`date_to` range
    - Language filter matches either question or answer language

- **GET** `/history/{history_id}` - Get exercise history record by ID
    - Path param: `history_id` - Exercise history record ID
    - Response: `ExerciseHistoryRead`
    - Returns detailed history record with full exercise information
    - Includes correct answer, options, translation, and explanation
    - Returns 404 if record not found or doesn't belong to authenticated user

### User Statistics

**Authentication required**

- **GET** `/users/me/statistics/` - Get user statistics overview
    - Query params:
        - `language` (optional) - Filter by language (ISO 639-1: en, uk, de, null = all languages)
        - `period` (optional) - Time period: `7d`, `30d`, `3m`, `1y`, `all` (default: `all`)
    - Response: `OverviewResponse`
    - Returns aggregated user metrics:
        - Total exercises completed (including and excluding skipped)
        - Overall accuracy percentage (from answered exercises only)
        - Current consecutive days streak
        - Whether at least one exercise was completed today
        - Total study time in hours
    - Without language filter: aggregates across all practiced languages
    - With language filter: shows statistics for that language only

- **GET** `/users/me/statistics/performance` - Get detailed performance statistics
    - Query params:
        - `language` (optional) - Filter by language (ISO 639-1: en, uk, de, null = all languages)
        - `period` (optional) - Time period: `7d`, `30d`, `3m`, `1y`, `all` (default: `all`)
    - Response: `PerformanceResponse`
    - Returns detailed performance metrics:
        - **by_difficulty**: Accuracy and mastery status per CEFR level (A1-C2)
        - **top_topics**: Top 5 topics by accuracy
        - **weak_topics**: Topics needing practice (accuracy < 60%, min 20 exercises)
        - **suggested_level**: Recommended next difficulty level (only when language specified)
    - Mastery criteria:
        - Difficulty level: accuracy ≥ 80% AND total ≥ 100 exercises
        - Topic status: mastered (85%+), good (70-85%), learning (50-70%), needs_practice (<50%)
    - Level recommendation criteria:
        - Comfortable zone: accuracy ≥ 70% AND total ≥ 10 exercises
        - Ready for next level: accuracy ≥ 80% AND total ≥ 50 exercises
        - Default: A1 for new learners with insufficient practice

---

## 🛠️ Tech Stack

**Core:**
- Python 3.11+
- FastAPI 0.118+
- SQLAlchemy 2.0 (async)
- PostgreSQL 14+
- Pydantic v2

**Infrastructure:**
- Alembic (database migrations)
- python-jose (JWT tokens)
- argon2-cffi (password hashing)
- Poetry (dependency management)

**Planned:**
- pytest (unit & integration testing)
- Docker & Docker Compose
- CI/CD pipeline

---

## 🧩 Current Progress

### ✅ Implemented

- **Database layer:**
    - SQLAlchemy 2.0 async models with relationships
    - Alembic migrations (12 revisions)
    - Database constraints (email format, positive time, translation completeness)
    - Optimized indexes (partial, composite, unique)
  
- **Schema layer:**
    - Pydantic v2 schemas with validation
    - Enums for languages, levels, exercise types, exercise status and user role
    - Business logic validation (password, exercise options, translations, exercise status)
    - Circular import resolution using TYPE_CHECKING
  
- **Core utilities:**
    - Application configuration (Pydantic Settings)
    - Async PostgreSQL connection
    - Security utilities (JWT, password hashing, Argon2)
    - Dependency injection with FastAPI
    - Helper functions: enum validation, date range parsing, option key extraction
    - Normalizers: topic formatting, answer cleanup
  
- **CRUD layer:**
    - Users: create, read by id/email/username, update, active language management
    - User languages: create, read, update, delete
    - Exercise: get topics, retrieve by criteria with spaced repetition
    - Exercise history: create submission records, retrieve with filters and pagination
  
- **Services layer:**
    - Authentication: user registration (simple & with language), login
    - User management: profile updates, password changes
    - User languages: add/update learning languages, delete
    - Exercise: retrieve practice exercises, validate and save submissions
    - Statistics: overview metrics, performance analysis, difficulty tracking
    - History: exercise history retrieval with filtering
  
- **API endpoints:**
    - Authentication: `/auth/register`, `/auth/register/complete`, `/auth/login`, `/auth/token`
    - User: `/users/me`, `/users/me/password`
    - Languages: `/users/me/languages`, `/users/me/languages/{language}`
    - Exercises: `/exercises/topics`, `/exercises/next`, `/exercises/{id}/submit`
    - History: `/history/`, `/history/{history_id}`
    - Statistics: `/users/me/statistics/`, `/users/me/statistics/performance`

### 🟡 In Development

- Admin panel for user and exercise management
- Bulk exercise import functionality

### 🔴 Planned

- Admin panel for exercise management
- Unit and integration tests (pytest)
- Docker setup
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
├── api/                             # Partially implemented
│   ├── endpoints/
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── exercises.py             # Exercise practice endpoints
│   │   ├── users.py                 # User management endpoints
│   │   ├── languages.py             # Language management endpoints
│   │   ├── statistics.py            # User learning statistics endpoints
│   │   └── user_exercise_history.py # User exercise history endpoints
│   └── dependencies.py              # Dependency injection
│
├── crud/                            # CRUD operations
│   ├── user.py              
│   ├── user_language.py
│   ├── exercise.py
│   └── user_exercise_history.py 
│
├── services/                        # Partially implemented
│   ├── __init__.py
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
│   ├── common.py                    # Shared schemas (Options)
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
git clone https://github.com/denysdontsu/language-learning-backend.git
cd language-learning-backend
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
API is in active development and subject to changes.

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

---

![Status](https://img.shields.io/badge/status-early%20development-yellow)

![Python](https://img.shields.io/badge/python-3.11+-blue)

![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0-green)

![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue)

**Version:** 0.1.0-alpha

**Last updated:** February 2026