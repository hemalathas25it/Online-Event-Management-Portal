## Software Requirements Specification (SRS)
Please paste the full contents of your `requirements.md` file so I can read it exactly as written.

I will:

* Read the requirements carefully.
* Use **only** the features listed in your file.
* **Not** add any extra features or assumptions beyond what is explicitly stated.
* Base all subsequent SRS sections strictly on your requirements.

### 1. Purpose and Scope

**Purpose:**
The purpose of this Online Event Management System is to provide a platform for users to register, log in, view events, register for events, and for administrators to manage users, events, and participant registrations.

**Scope:**
The system supports basic event management using Python and SQLite. It provides separate functions for users and administrators while focusing only on the required features for the first version.

**In Scope**

* User registration and login
* Create, edit, and delete events
* View upcoming and past events
* Online event registration
* Manage participant registrations
* Admin dashboard for managing users and events

**Out of Scope (Version 1)**

* Online payment processing
* Email or SMS notifications
* Social media integration
* Event ticket generation
* QR code check-in
* Mobile application
* Reports and analytics
* Multi-language support

---

## 2. Functional Requirements

* **FR-01:** The system shall allow users to register and log in using valid credentials.
* **FR-02:** The system shall allow administrators to create, edit, and delete events.
* **FR-03:** The system shall allow users to view upcoming and past events.
* **FR-04:** The system shall allow users to register for available events online.
* **FR-05:** The system shall allow administrators to manage participant registrations.
* **FR-06:** The system shall provide an admin dashboard for managing users and events.

---

## 3. Non-Functional Requirements

* **NFR-01:** The system shall display any page within **3 seconds** for **95%** of requests under normal usage.
* **NFR-02:** The system shall store all user passwords using a **secure hashed algorithm** and require **100%** of login requests to be authenticated before access is granted.
* **NFR-03:** The system shall allow a new user to complete registration in **3 minutes or less** without referring to documentation.
* **NFR-04:** The system shall achieve at least **99% availability** during scheduled operating hours.
* **NFR-05:** The SQLite database shall successfully save and retrieve **100%** of valid records without data corruption.
* **NFR-06:** The system shall recover from unexpected application shutdowns without losing previously saved data.

---

## 4. Assumptions

* Users have access to a computer with a web browser.
* Users have a stable internet connection.
* Administrators are responsible for creating and managing event information.
* The Python runtime and SQLite database are correctly installed.
* Each user has unique login credentials.
* The SQLite database is sufficient for the expected number of users and events.

---

## 5. Constraints

* The system must be developed using **Python**.
* The system must use **SQLite** as the database.
* The application will use a **single local SQLite database**.
* The project will be developed within the available project schedule and resources.
* The system will support only the features specified in the project requirements.
* No external database servers or paid cloud services will be used.
