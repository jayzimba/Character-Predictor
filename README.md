# Personality Classification Using Data Mining

An intelligent web platform that collects behavioural assessment responses, transforms them into numerical features, and classifies personality into one of four temperament types using classical data-mining algorithms.

**Personality classes:** Choleric · Melancholic · Phlegmatic · Sanguine

> This assessment is intended for educational, research and personal-development purposes and should not be considered a clinical psychological diagnosis.

---

## Problem addressed

Manual personality assessment is slow, inconsistent, and easy to bias. This system standardises data collection (a versioned Likert questionnaire stored in MySQL) and applies supervised classification (Decision Tree, Naive Bayes, KNN) so that results are reproducible and comparable.

## Objectives

- Collect behavioural data through a configurable questionnaire.
- Engineer category-level features from Likert responses.
- Train, evaluate and compare three classifiers on the same split.
- Serve predictions through a secured REST API.
- Present results and research metrics in professional user and admin interfaces.

## Features

**User:** register, login, profile, take/save/submit assessment, view prediction and personality mix, history, print/download result.

**Administrator:** user and question management, assessment overview, model training and comparison, activate best model, analytics, audit logs.

Full feature delivery follows the phased roadmap in `docs/ARCHITECTURE.md`.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, Tailwind CSS, React Router, Axios, Recharts |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, JWT |
| Machine learning | pandas, NumPy, scikit-learn, joblib |
| Database | MySQL |

## Architecture

Presentation (React) → REST API (FastAPI) → MySQL + ML engine (scikit-learn) → prediction stored and shown on the dashboard.

Questionnaire **scoring** (feature engineering) is separate from **classification** (trained model). A rule-based path, if present, is labelled DEMO MODE only.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the ERD, workflows, API plan and defence notes.

## Project structure

```
├── docs/                 Architecture and academic design
├── backend/              FastAPI application, ML package, tests
└── frontend/             React + Vite SPA
```

## Installation

Prerequisites:

- Python 3.11 or newer
- Node.js 18 or newer and npm
- MySQL 8 (required to apply migrations; schema tests use SQLite)

### Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)  
Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App: [http://127.0.0.1:5173](http://127.0.0.1:5173)

The Vite dev server proxies `/api` to FastAPI.

Public routes: `/`, `/about`, `/personality-types`, `/login`, `/register`.  
Signed-in user: `/app`, `/app/assessment`, `/app/history`, `/app/profile`.  
Admin only: `/admin` and its sidebar pages, including `/admin/dataset` for CSV validation.  
Developer checks remain at `/dev`.

### Database setup

1. Install MySQL 8 and make sure the server is running.
2. Edit `backend/.env` so `DATABASE_URL` matches your local user. This machine’s default is passwordless root:

   `mysql+pymysql://root@127.0.0.1:3306/personality_classification`

3. From `backend/` with the virtualenv active:

```bash
python -c "from app.database.session import ensure_database_exists; ensure_database_exists()"
alembic upgrade head
python -m app.database.seed
```

The seed is idempotent. It creates roles, four personality types, 16 categories, 32 Likert questions, and two local demo accounts.

### ML training

Phase 10 prepares features. Phase 11 fits Decision Tree, Naive Bayes and KNN on the training fold. From `backend/` with the virtualenv active:

```bash
python -m app.ml.dataset.generate_demo
```

That writes a bundled `DEMO/SYNTHETIC` CSV. Administrators validate it at `/admin/dataset`, train at `/admin/training`, and evaluate at `/admin/models`. Users classify a completed assessment with `POST /api/predictions/classify`. The detailed results page is **Phase 14**.

### Running the application

Start FastAPI and Vite as above. Applying migrations is optional for the Phase 2 health screen; it is required before Phase 3.

### Testing

```bash
cd backend
source .venv/bin/activate
pytest
```

Frontend tests will be added when UI flows exist.

## Screenshots

_Placeholders — add after the UI phases._

- Landing page
- User dashboard
- Assessment flow
- Results page
- Admin dashboard
- Model comparison

## API endpoints

Implemented through Phase 13:

| Method | Path | Description |
|---|---|---|
| GET | `/` | API metadata |
| GET | `/api/health` | Process liveness |
| GET | `/api/health/ready` | MySQL readiness |
| GET | `/api/personality-types` | Public educational catalogue |
| POST | `/api/auth/register` | Create a USER account and return a JWT |
| POST | `/api/auth/login` | Email + password → JWT |
| GET | `/api/auth/me` | Current user (Bearer token) |
| POST | `/api/auth/password-reset/request` | Issues a hashed reset token (raw token only if `APP_DEBUG=true`) |
| POST | `/api/auth/password-reset/confirm` | Set a new password with the reset token |
| GET / PATCH | `/api/users/me` | View or update own profile |
| GET | `/api/users/me/dashboard` | Assessment counts, last result and stored mix |
| POST | `/api/users/me/password` | Change password while signed in |
| GET | `/api/admin/users` | List users (ADMIN only) |
| GET | `/api/questions` | Active Likert instrument (authenticated; no scoring metadata) |
| GET | `/api/admin/questions` | Full question catalogue including weight and reverse scoring |
| POST | `/api/assessments` | Start or resume an in-progress assessment (consent required) |
| GET | `/api/assessments` | List the caller's assessments |
| GET | `/api/assessments/{id}` | Assessment plus saved Likert values (owner only) |
| POST | `/api/assessments/{id}/answers` | Save or update answers; weighted scores stay on the server |
| POST | `/api/assessments/{id}/submit` | Mark complete when every active item is answered |
| GET | `/api/admin/datasets/demo` | Bundled DEMO/SYNTHETIC dataset metadata (ADMIN) |
| POST | `/api/admin/datasets/demo/validate` | Validate the bundled CSV into category features (ADMIN) |
| POST | `/api/admin/datasets/validate` | Upload a CSV and run the same preprocessor (ADMIN) |
| POST | `/api/admin/datasets/from-assessments` | Map completed assessments to category features (ADMIN) |
| GET | `/api/admin/models/training` | Last training run metadata (ADMIN) |
| POST | `/api/admin/models/train/demo` | Fit DT, NB and KNN on the bundled DEMO split (ADMIN) |
| POST | `/api/admin/models/train` | Fit the same three algorithms on an uploaded CSV (ADMIN) |
| GET | `/api/admin/models` | Registry rows with stored sklearn metrics (ADMIN) |
| GET | `/api/admin/models/evaluation` | Last held-out comparison (ADMIN) |
| POST | `/api/admin/models/evaluate/demo` | Score the DEMO test fold and register models (ADMIN) |
| POST | `/api/admin/models/evaluate` | Score an uploaded CSV's test fold and register models (ADMIN) |
| POST | `/api/admin/models/activate-selected` | Make the last evaluation winner ACTIVE (ADMIN) |
| POST | `/api/admin/models/{id}/activate` | Make one registered model ACTIVE (ADMIN) |
| POST | `/api/predictions/classify` | Classify a completed assessment (owner or ADMIN) |
| GET | `/api/predictions/{assessment_id}` | Stored prediction for that assessment (owner or ADMIN) |

Planned groups: `/api/analytics`.

## Security

- Passwords are hashed with bcrypt. Never stored in plaintext.
- JWT access tokens; role checks on the server.
- Secrets live in `.env` (not committed). Use `.env.example` as the template.
- SQLAlchemy parameterised queries; Pydantic validation at the boundary.

## Privacy and ethics

- Consent is required before an assessment (implemented with the questionnaire flow).
- Optional demographics only; prefer age group over date of birth.
- Results use language such as “Your assessment indicates…” — not absolute diagnosis.
- Synthetic training data, if used, is labelled DEMO/SYNTHETIC and must not be reported as research findings.

## Limitations

- No real labelled clinical dataset is assumed. Early models may use clearly marked synthetic data.
- Four-temperament labels are a simplified educational model.
- The user dashboard is live; it stays empty until assessments exist. The admin dashboard is still a placeholder.
- Password-reset tokens are returned in the API only while `APP_DEBUG=true`. Production would email them.
- Schema tests run on SQLite; production target remains MySQL.

## Future enhancements

- Replace synthetic data with ethically collected labelled assessments.
- Additional algorithms or ensemble comparison.
- Deployment (container or campus server) and HTTPS.
- Optional multi-language questionnaire.

## Development credentials

Local/demo only. **Never use these passwords on a deployed system.**

| Role | Email | Password |
|---|---|---|
| ADMIN | admin@temperamentlab.local | AdminDemo123! |
| USER | user@temperamentlab.local | DemoUser123! |

Passwords are stored as bcrypt hashes. Use these accounts on `/login`.

## Licence

Academic / coursework use.
