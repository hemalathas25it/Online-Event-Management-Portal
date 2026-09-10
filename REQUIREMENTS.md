# Requirements Document: Online Event Management System

## 1. System Overview
The Online Event Management System is a lightweight, responsive web application designed for managing college and organizational events. It provides separate capabilities for standard users (viewing events, registering for events) and administrators (creating/editing/deleting events, viewing all users, managing registrations, accessing dashboard metrics and summary reports).

---

## 2. Functional Requirements

### FR-01: User Registration & Authentication
- The system shall allow new users to register with a unique username and a secure password.
- The system shall authenticate users using secure credentials and issue session tokens (JWT).
- The system shall differentiate between regular users and administrators.
- The system shall allow users to log out safely and invalidate client sessions.

### FR-02: Event Management (Admin CRUD)
- Administrators shall be able to create new events with title, description, date, and location.
- Administrators shall be able to edit details of existing events.
- Administrators shall be able to delete events, cascading to remove associated registrations.

### FR-03: Event Browsing & Search
- Users and administrators shall be able to view upcoming events and past events in distinct sections.
- The system shall allow users to search events by title or keyword in real time.
- The system shall indicate the status of each event (Upcoming vs. Past).

### FR-04: Online Event Registration
- Authenticated users shall be able to register for available upcoming events.
- The system shall validate that an event is in the future before permitting registration.
- The system shall prevent duplicate registrations for the same user and event.

### FR-05: Participant Registration Management
- Administrators shall be able to view all participant registrations across all events.
- Administrators shall be able to search and filter registrations by participant or event name.
- Administrators shall be able to remove/cancel participant registrations.

### FR-06: Admin Dashboard & Reports
- The system shall provide an administrator dashboard displaying key metrics:
  - Total upcoming events
  - Total past events
  - Total participant registrations
  - Total registered users
- The dashboard shall provide summary reports of event-wise participant registration counts and distributions.
- The dashboard shall provide quick-action links to manage events, participants, and users.

---

## 3. Non-Functional Requirements

### NFR-01: Performance
- The system shall process API requests and render views within 3 seconds under normal usage.

### NFR-02: Security
- Passwords must be hashed using a standard secure algorithm (`bcrypt`).
- Protected endpoints must enforce token authentication and role-based authorization.
- Input validation must prevent malicious inputs or duplicate entries.

### NFR-03: Usability
- The user interface must be clean, modern, intuitive, and responsive across desktop and mobile screen sizes.
- A new user must be able to complete registration and register for an event within 3 minutes without external guidance.

### NFR-04: Reliability & Data Integrity
- The system must use an ACID-compliant local SQLite database with Write-Ahead Logging (WAL) enabled.
- Data must survive unexpected shutdowns and application restarts.

---

## 4. Technology Stack & Constraints
- **Backend**: Python 3.10+ / FastAPI / Uvicorn
- **Database**: SQLite3 (Local file database)
- **Frontend**: HTML5, CSS3, Modern ES6 JavaScript (No bulky external frameworks)
- **Scope Constraints**: No external payment processing, no SMS/email gateways, no QR code generation, no cloud database dependencies.
