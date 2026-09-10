# Online Event Management System (EventHub)

A full-stack, responsive Event Management System built strictly adhering to the Software Requirements Specification (`srs.md`) and `REQUIREMENTS.md`. It features a FastAPI Python backend, SQLite database with Write-Ahead Logging (WAL), JWT authentication, role-based authorization, real-time search, interactive administrative dashboards, and summary reporting.

---

## 🌟 Key Features

- **Authentication & Security (FR-01, NFR-02)**:
  - User registration and login with secure password hashing (`bcrypt`).
  - Stateless JSON Web Token (JWT) session authorization.
  - Role-based access control distinguishing Standard Users and Administrators.
- **Event Management CRUD (FR-02)**:
  - Administrators can create, view, update, and delete campus events.
  - Automatic cascading deletion of associated registrations when an event is removed.
- **Event Browsing & Live Search (FR-03)**:
  - Separate views for Upcoming and Past events.
  - Instant live debounced search across event titles, descriptions, and locations.
- **Online Event Registration (FR-04)**:
  - Interactive event picker and registration form.
  - Automatic validation preventing registration for past events and duplicate sign-ups.
- **Participant Registration Management (FR-05)**:
  - Administrators can inspect, filter, and cancel participant registrations across all events.
  - Standard users can track and cancel their personal event bookings in "My Registrations".
- **Admin Dashboard & Reports (FR-06)**:
  - Real-time statistics counters for upcoming events, past events, total registrations, and users.
  - Event-wise registration breakdown and recent registration activity logs.
- **Modern Responsive UI**:
  - Polished desktop layout with sticky navigation and mobile off-canvas drawer.
  - Toast notification system for clear user feedback.

---

## 🏗️ Project Architecture

```
Online-Event-Management-Portal/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & static mounting
│   ├── database.py              # SQLite connection, WAL mode, schema & seed logic
│   ├── auth.py                  # bcrypt password hashing & JWT security dependencies
│   ├── models.py                # Pydantic data schemas & request validation
│   └── routers/
│       ├── __init__.py
│       ├── auth_router.py       # /api/auth (register, login, me)
│       ├── events_router.py     # /api/events (CRUD, filters, search)
│       ├── registrations_router.py # /api/registrations (registration & cancellation)
│       ├── users_router.py      # /api/users (user directory)
│       └── dashboard_router.py  # /api/dashboard (stats & reports)
├── frontend/
│   ├── index.html               # Responsive single-page application UI
│   ├── style.css                # Modern CSS design system
│   └── script.js                # API integration & reactive state management
├── tests/
│   ├── __init__.py
│   └── test_api.py              # Automated Pytest test suite (15 test cases)
├── events.db                    # SQLite local database (generated on startup)
├── requirements.txt             # Python dependencies
├── srs.md                       # Software Requirements Specification
├── REQUIREMENTS.md              # Extracted requirements document
└── README.md                    # Setup and run instructions
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- Web browser (Chrome, Edge, Firefox, Safari)

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the unified application with Uvicorn:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Or directly with Python:
```bash
python -m backend.main
```

The application will be accessible at:
- **Web Application UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Default Credentials

The database automatically initializes and seeds demo accounts upon the first run:

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full Dashboard, Manage Events (CRUD), View all Users, Manage all Registrations, Summary Reports |
| **Standard User** | `student01` | `student123` | Browse Upcoming & Past Events, Register for Events, My Registrations |

> You can also register new user accounts anytime via the **Sign In / Register** portal.

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:
```bash
pytest tests/ -v
```

This verifies:
- User registration, password hashing, and authentication tokens
- Invalid credential rejection and duplicate username prevention
- Event CRUD operations and administrator permission enforcement
- Upcoming and past event filtering and keyword searching
- Event registration, duplicate prevention, and past event restrictions
- Dashboard counters, metrics, and summary reporting
- User listing restricted to administrators
