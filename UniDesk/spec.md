# UniDesk

## 1. Project Goal

The goal of UniDesk is to build a small but complete internal ticketing system that demonstrates the ability to use an AI agent to build a real full-stack application. The system will allow authenticated users to manage support tickets and comments through a React client, FastAPI API, and PostgreSQL database. The project will focus on a clear specification, reliable functionality, input validation, authentication, and tested API behavior.

## 2. Problem Statement

IT support requests in an organization can become difficult to track when they are reported through informal channels such as messages, emails, or verbal communication. This can lead to lost requests, unclear status, and difficulty in maintaining communication between employees and support staff. UniDesk addresses this problem by providing a centralized system where users can securely submit, track, and manage IT support tickets and related comments.

## 3. Scope

### In Scope

- **User Registration & Pre-verification**:
  - Sign-up requiring official Name, Company Email, Password, and Role selection (`Employee` or `Support Agent`).
  - Strict registration validation against a backend pre-approved company employee whitelist (Name and Email matching). Unrecognized credentials are rejected (`400 Bad Request`).
- **Authentication & Security**:
  - Secure login using registered credentials (Name/Email and Password).
  - Stateless JWT (JSON Web Token) authentication for managing user sessions and authorization headers.
- **Role-Based Access Control (RBAC)**:
  - **Employee**:
    - Can create new tickets with title, description, and initial priority level.
    - Can view all tickets and access overall ticket statistics dashboard.
    - Can add comments **only** to tickets they created.
    - Can update and delete **only** their own tickets.
  - **Support Agent**:
    - Can view all system tickets and dashboard statistics.
    - Can update ticket status (`open`, `in_progress`, `resolved`, `closed`) and priority (`low`, `medium`, `high`).
    - Can post comments on **any** ticket.
    - Cannot create new tickets.
- **Dashboard & Filtering**:
  - Global overview of total, open, in-progress, resolved, and closed ticket statistics.
  - Filterable ticket views by status: `All`, `Open`, `In Progress`, `Resolved`, and `Closed`.
  - Visual priority indicators (`low`, `medium`, `high`).
- **Data & System Architecture**:
  - PostgreSQL relational database using strictly 3 core tables: `users`, `tickets`, and `comments`.
  - FastAPI backend providing RESTful endpoints with input validation and schema enforcement via Pydantic.
  - React (Vite + Tailwind CSS) frontend with dedicated routes for Login, Register, Ticket List, and Ticket Detail views.
- **Testing & Quality Control**:
  - Automated backend API testing using `pytest` achieving a minimum target of **>70% test coverage**.

### Out of Scope

- External notifications via Email, SMS, or third-party webhooks.
- File, document, or image attachments on tickets or comments.
- Real-time communication via WebSockets or live messaging.
- Native mobile applications (iOS/Android).
- Payment gateways or billing features.
- Automated AI chatbot assistants or custom statistical report exports.

## 4. Users and Roles

The system enforces strict Role-Based Access Control (RBAC) to decouple standard ticket creation from resolution and administrative management. There are two primary user roles:

### 4.1 Employee

- **Target Audience**: Internal company staff requiring IT or administrative assistance.
- **Onboarding**: Self-registers using pre-approved Name and Company Email verified against the company whitelist, assigning themselves the `Employee` role.
- **Permissions & Capabilities**:
  - **Create**: Can submit new tickets by providing a title, detailed description, and initial priority level (`low`, `medium`, `high`).
  - **Read**: Can view all tickets in the system and see aggregate dashboard statistics.
  - **Update/Delete**: Can edit or delete **only** the tickets created by their own account.
  - **Comment**: Can post comments **only** on tickets they created.
- **Restrictions**: Cannot alter ticket statuses (`open`, `in_progress`, `resolved`, `closed`) or modify ticket priority after creation.

### 4.2 Support Agent

- **Target Audience**: Dedicated IT, Operations, or Support personnel responsible for resolving issues.
- **Onboarding**: Registers using pre-approved Agent credentials (Name and Email verified against the backend Agent whitelist), selecting the `Support Agent` role.
- **Permissions & Capabilities**:
  - **Read**: Global read access to all tickets, full comment threads, and overall ticket metrics.
  - **Update**: Can update ticket status (`open`, `in_progress`, `resolved`, `closed`) and adjust ticket priority levels (`low`, `medium`, `high`).
  - **Comment**: Can post responses/comments on **any** ticket across the system.
- **Restrictions**: Cannot create new tickets; cannot edit or delete comments posted by other users.

### 4.3 Summary Matrix

| Capability                        | Employee               | Support Agent          |
| :-------------------------------- | :--------------------- | :--------------------- |
| **Registration**                  | Pre-approved Whitelist | Pre-approved Whitelist |
| **Create Tickets**                | ✅ Yes                 | ❌ No                  |
| **View All Tickets**              | ✅ Yes                 | ✅ Yes                 |
| **Edit/Delete Own Tickets**       | ✅ Yes                 | ❌ No                  |
| **Update Ticket Status/Priority** | ❌ No                  | ✅ Yes                 |
| **Comment on Own Tickets**        | ✅ Yes                 | ✅ Yes                 |
| **Comment on Any Ticket**         | ❌ No                  | ✅ Yes                 |

## 5. Core Features

### 5.1 User Authentication & Onboarding

- **Pre-verified Registration**:
  - Users submit their official Name, Company Email, Password, and Role (`Employee` or `Support Agent`).
  - Backend matches Name and Email against a pre-configured company whitelist before creating the account.
  - Rejects unauthorized registration attempts with a `400 Bad Request` error.
- **JWT-Based Authentication**:
  - Secure sign-in yielding a JSON Web Token (JWT) containing encoded `user_id` and `role`.
  - Frontend stores token securely and attaches it to authorization headers for protected API requests.

### 5.2 Ticket Management & Lifecycle

- **Ticket Creation (Employees Only)**:
  - Form inputs: Title, Description, and Priority (`low`, `medium`, `high`).
  - Auto-assigns creator ID (`created_by`), sets initial status to `open`, and records timestamp.
- **Ticket Resolution & Status Updates (Support Agents Only)**:
  - Agents transition ticket status across valid lifecycle states: `open` → `in_progress` → `resolved` → `closed`.
  - Agents can elevate or lower ticket priority based on issue urgency.
- **Ticket Modification & Deletion (Employees Only)**:
  - Employees can edit or permanently delete tickets **only** if they created them.

### 5.3 Communication & Discussion

- **Contextual Commenting**:
  - Employees can post comments **only** on tickets they authored.
  - Support Agents can post responses and updates on **any** ticket.
  - Displays commenter name, role badge (`Employee` / `Support Agent`), and timestamp.

### 5.4 Dashboard & View Controls

- **Statistics Overview**:
  - Real-time metrics bar displaying counts for: Total, Open, In Progress, Resolved, and Closed tickets.
- **Status Filtering**:
  - Quick-filter tabs (`All`, `Open`, `In Progress`, `Resolved`, `Closed`) to narrow down ticket lists.
- **Priority Visuals**:
  - Color-coded badges indicating issue severity (`low` = green/blue, `medium` = yellow/orange, `high` = red).

## 6. Data Model & Schema

The application uses PostgreSQL with strictly **3 relational tables**: `users`, `tickets`, and `comments`. Database migrations are managed via Alembic.

### 6.1 Entity Relationship Diagram (Conceptual)

- **`users`** 1 ───< **`tickets`** (One user creates many tickets)
- **`users`** 1 ───< **`comments`** (One user posts many comments)
- **`tickets`** 1 ───< **`comments`** (One ticket holds many comments)

### 6.2 Table Definitions

#### `users` Table

Stores registered employee and support agent accounts.

| Column Name     | Data Type      | Constraints                            | Description                                  |
| :-------------- | :------------- | :------------------------------------- | :------------------------------------------- |
| `id`            | `INTEGER`      | Primary Key, Auto-Increment            | Unique user identifier                       |
| `name`          | `VARCHAR(100)` | NOT NULL                               | User's full official name                    |
| `email`         | `VARCHAR(255)` | UNIQUE, NOT NULL, Index                | Official company email address               |
| `password_hash` | `VARCHAR(255)` | NOT NULL                               | Securely hashed password (Bcrypt/Argon2)     |
| `role`          | `VARCHAR(20)`  | NOT NULL, Default: `'employee'`        | User role: `'employee'` or `'support_agent'` |
| `created_at`    | `TIMESTAMP`    | NOT NULL, Default: `CURRENT_TIMESTAMP` | Account creation timestamp                   |

#### `tickets` Table

Stores issue tickets submitted by employees.

| Column Name   | Data Type      | Constraints                            | Description                                                          |
| :------------ | :------------- | :------------------------------------- | :------------------------------------------------------------------- |
| `id`          | `INTEGER`      | Primary Key, Auto-Increment            | Unique ticket identifier                                             |
| `title`       | `VARCHAR(200)` | NOT NULL                               | Short summary of the issue                                           |
| `description` | `TEXT`         | NOT NULL                               | Detailed description of the issue                                    |
| `status`      | `VARCHAR(20)`  | NOT NULL, Default: `'open'`            | Lifecycle state: `'open'`, `'in_progress'`, `'resolved'`, `'closed'` |
| `priority`    | `VARCHAR(10)`  | NOT NULL, Default: `'medium'`          | Severity level: `'low'`, `'medium'`, `'high'`                        |
| `created_by`  | `INTEGER`      | Foreign Key (`users.id`), NOT NULL     | User ID of the employee who created the ticket                       |
| `created_at`  | `TIMESTAMP`    | NOT NULL, Default: `CURRENT_TIMESTAMP` | Ticket creation timestamp                                            |
| `updated_at`  | `TIMESTAMP`    | NOT NULL, Default: `CURRENT_TIMESTAMP` | Timestamp of last modification                                       |

#### `comments` Table

Stores response threads linked to specific tickets.

| Column Name  | Data Type   | Constraints                                   | Description                        |
| :----------- | :---------- | :-------------------------------------------- | :--------------------------------- |
| `id`         | `INTEGER`   | Primary Key, Auto-Increment                   | Unique comment identifier          |
| `ticket_id`  | `INTEGER`   | Foreign Key (`tickets.id`), On Delete CASCADE | Associated ticket ID               |
| `user_id`    | `INTEGER`   | Foreign Key (`users.id`), NOT NULL            | User ID of the commenter           |
| `content`    | `TEXT`      | NOT NULL                                      | Comment message body               |
| `created_at` | `TIMESTAMP` | NOT NULL, Default: `CURRENT_TIMESTAMP`        | Timestamp when comment was created |

## 7. API Endpoints

All endpoints are hosted under the `/api/v1` base route. Protected routes require a valid JWT passed in the `Authorization: Bearer <token>` header.

### 7.1 Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint         | Access    | Description                                                           |
| :----- | :--------------- | :-------- | :-------------------------------------------------------------------- |
| `POST` | `/auth/register` | Public    | Register new user (validates Name & Email against company whitelist). |
| `POST` | `/auth/login`    | Public    | Authenticate user credentials and return JWT token.                   |
| `GET`  | `/auth/me`       | Protected | Return current authenticated user profile and role details.           |

### 7.2 Ticket Management Endpoints (`/api/v1/tickets`)

| Method   | Endpoint               | Access                | Description                                                                         |
| :------- | :--------------------- | :-------------------- | :---------------------------------------------------------------------------------- |
| `GET`    | `/tickets`             | Protected (All)       | List all tickets. Supports optional query parameters `?status=` and `?priority=`.   |
| `GET`    | `/tickets/stats`       | Protected (All)       | Get aggregate ticket counts (`total`, `open`, `in_progress`, `resolved`, `closed`). |
| `POST`   | `/tickets`             | Employee Only         | Create a new ticket (Title, Description, Priority).                                 |
| `GET`    | `/tickets/{id}`        | Protected (All)       | Retrieve detailed information for a specific ticket.                                |
| `PUT`    | `/tickets/{id}`        | Employee Only (Owner) | Update ticket title, description, or priority. Allowed **only** by ticket author.   |
| `PATCH`  | `/tickets/{id}/status` | Support Agent Only    | Update ticket status (`open`, `in_progress`, `resolved`, `closed`) or priority.     |
| `DELETE` | `/tickets/{id}`        | Employee Only (Owner) | Delete a ticket. Allowed **only** by the employee who created it.                   |

### 7.3 Comment Endpoints (`/api/v1/tickets/{id}/comments`)

| Method | Endpoint                 | Access                  | Description                                                                                                           |
| :----- | :----------------------- | :---------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/tickets/{id}/comments` | Protected (All)         | Fetch all comments associated with a specific ticket in chronological order.                                          |
| `POST` | `/tickets/{id}/comments` | Restricted (Role-based) | Add a comment to a ticket. Employees can comment **only on their own tickets**; Agents can comment on **any ticket**. |

## 8. Business & Validation Rules

This section outlines the strict validation constraints and domain rules enforced at both API (Pydantic schemas) and Database levels.

### 8.1 Registration & Whitelist Rules

- **Whitelist Enforcement**: The system compares submitted `name` and `email` during sign-up against a pre-configured array of allowed company employees (`MOCK_EMPLOYEE_WHITELIST`).
  - If no matching `name` + `email` pair is found, the backend raises `400 Bad Request` (`"Registration denied: Name or email not found in company records."`).
- **Case-Insensitive Matching**: Employee name comparison must ignore leading/trailing whitespace and case sensitivity (`John Doe` matches `john doe`).
- **Email Constraints**: Must be a valid email format ending in official company domain. Duplicates in the `users` table are rejected (`409 Conflict`).
- **Password Validation**: Minimum length of 8 characters containing at least one number and one uppercase letter. Stored using Bcrypt hashing (`passlib`).

### 8.2 Authorization & Role-Based Rules (RBAC)

- **Ticket Creation**: Restricted to `role == 'employee'`. Support Agents attempting to post to `/tickets` receive `403 Forbidden`.
- **Ticket Modification & Deletion**:
  - An employee can edit (`PUT`) or delete (`DELETE`) a ticket **only** if `ticket.created_by == current_user.id`.
  - Unmatching owner IDs receive `403 Forbidden` (`"You can only modify or delete your own tickets."`).
- **Ticket Status & Priority Updates**:
  - Changing `status` (`open`, `in_progress`, `resolved`, `closed`) or adjusting `priority` via `/tickets/{id}/status` is restricted **exclusively** to `role == 'support_agent'`.
  - Employees attempting status updates receive `403 Forbidden`.
- **Comment Authorization**:
  - **Support Agents**: Allowed to post comments on **any** ticket ID.
  - **Employees**: Allowed to post comments **only** if `ticket.created_by == current_user.id`. Employee attempts to comment on someone else's ticket receive `403 Forbidden`.

### 8.3 Input Data Validation

- **Tickets**:
  - `title`: Non-empty string, min 5 chars, max 200 chars.
  - `description`: Non-empty text, min 10 chars.
  - `priority`: Must be one of `['low', 'medium', 'high']`. Default: `'medium'`.
  - `status`: Must be one of `['open', 'in_progress', 'resolved', 'closed']`. Default: `'open'`.
- **Comments**:
  - `content`: Non-empty text, min 1 char, max 2000 chars.

## 9. Frontend Architecture & Views

The client application is built with React, Vite, and Tailwind CSS using standard Client-Side Routing (`react-router-dom`). It manages session state via a lightweight Context API (`AuthContext`) that stores the JWT token in `localStorage`.

### 9.1 View / Route Map

| Route          | Access        | Component          | Key Responsibilities                                                                             |
| :------------- | :------------ | :----------------- | :----------------------------------------------------------------------------------------------- |
| `/login`       | Public        | `LoginView`        | Renders sign-in form. On success, saves JWT and redirects to `/dashboard`.                       |
| `/register`    | Public        | `RegisterView`     | Form for Name, Email, Password, and Role selection. Displays error if whitelist match fails.     |
| `/dashboard`   | Protected     | `DashboardView`    | Main hub. Displays aggregate metrics bar, status filter tabs, and the searchable ticket list.    |
| `/tickets/new` | Employee Only | `CreateTicketView` | Form to submit a new ticket (Title, Description, Priority). Hidden from Support Agents.          |
| `/tickets/:id` | Protected     | `TicketDetailView` | Displays complete ticket thread, status/priority update controls (for Agents), and comment feed. |

### 9.2 Key Component Hierarchy

### 9.2 Key Component Hierarchy

```text
src/
├── components/
│   ├── common/
│   │   ├── Navbar.jsx           # Dynamic navigation header with User Profile & Logout
│   │   ├── ProtectionRoute.jsx  # Auth & Role-based route guard wrapper
│   │   └── StatusBadge.jsx      # Color-coded badges for status & priority
│   ├── dashboard/
│   │   ├── MetricsBar.jsx       # Real-time counter cards (Total, Open, Resolved, etc.)
│   │   ├── FilterTabs.jsx       # Tab controls to filter tickets by status
│   │   └── TicketCard.jsx       # Individual ticket preview card in list view
│   └── tickets/
│       ├── CommentThread.jsx     # Chronological list of ticket comments
│       ├── CommentForm.jsx       # Input field to add comments (with role restriction logic)
│       └── AgentControls.jsx     # Dropdown menus for agents to update Status & Priority
├── context/
│   └── AuthContext.jsx          # Holds user, token, role, login(), and logout() state
└── views/                       # Pages corresponding to Route Map
```

### 9.3 UI/UX Specifications & Role Adaptations

- **Global Navigation (Navbar)**:
  - Displays user name, role badge (`Employee` vs `Support Agent`), and Logout button.
  - Shows **"+ Create Ticket"** CTA button **only** when logged in as an `Employee`.
- **Ticket List (DashboardView)**:
  - Interactive status filter tabs (`All`, `Open`, `In Progress`, `Resolved`, `Closed`).
  - Cards display title, snippet, status badge, priority indicator, timestamp, and author name.
- **Detail Page (TicketDetailView)**:
  - **Support Agent View**: Shows editable dropdown controls to instantly update ticket `status` or `priority`.
  - **Employee View**: Hides status change dropdowns; shows edit/delete action buttons **only** if `created_by == current_user.id`.
  - **Comment Form**: Displays dynamic placeholder/disabled state if an employee attempts to view a ticket created by someone else.

## 10. Error Handling & HTTP Status Codes

The API enforces uniform, JSON-formatted error responses for all failed operations using FastAPI's standard exception format:

````json
{
  "detail": "Human-readable error explanation message."
}

{
  "detail": "Registration denied: Name or email not found in company records."
}

{
  "detail": "Access denied: Support Agents are not allowed to create tickets."
}

{
  "detail": "Forbidden: You are only allowed to modify or delete your own tickets."
}

{
  "detail": [
    {
      "loc": ["body", "status"],
      "msg": "value is not a valid enumeration member; permitted: 'open', 'in_progress', 'resolved', 'closed'",
      "type": "type_error.enum"
    }
  ]
} 


