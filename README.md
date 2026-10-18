# BookLoop --- Campus Book Marketplace

> A student-focused platform for buying, selling, exchanging, and
> donating used academic books within a campus community.

BookLoop is designed to make academic books easier to discover and
reuse. Students can publish book listings, explore available books,
review book details, make offers, manage incoming and outgoing offers,
save books to a wishlist, and manage their profile and activity from a
dashboard.

This README documents the project purpose, features, architecture,
modules, data model, workflows, setup, testing checklist, security
considerations, and possible future improvements.

> **Implementation note:** This documentation is based on the project
> structure and implementation details available so far. Confirm the
> exact API routes, database configuration, and current feature behavior
> against `backend/app.py`, `backend/schema.sql`, `run.py`, and the
> JavaScript files before treating every endpoint or setup detail as
> definitive.

------------------------------------------------------------------------

## Table of Contents

-   [1. Project Overview](#1-project-overview)
-   [2. Problem Statement](#2-problem-statement)
-   [3. Goals and Scope](#3-goals-and-scope)
-   [4. Core Features](#4-core-features)
-   [5. Technology Stack](#5-technology-stack)
-   [6. Repository Structure](#6-repository-structure)
-   [7. System Architecture](#7-system-architecture)
-   [8. Application Modules](#8-application-modules)
-   [9. User Roles and Permissions](#9-user-roles-and-permissions)
-   [10. Main User Journeys](#10-main-user-journeys)
-   [11. Book and Offer Lifecycles](#11-book-and-offer-lifecycles)
-   [12. Data Model](#12-data-model)
-   [13. Database Relationship
    Diagram](#13-database-relationship-diagram)
-   [14. Request and Response Flow](#14-request-and-response-flow)
-   [15. Local Installation](#15-local-installation)
-   [16. Configuration](#16-configuration)
-   [17. Database Setup](#17-database-setup)
-   [18. Running BookLoop](#18-running-bookloop)
-   [19. Application Pages](#19-application-pages)
-   [20. API Documentation Guide](#20-api-documentation-guide)
-   [21. Validation and Business
    Rules](#21-validation-and-business-rules)
-   [22. Error Handling](#22-error-handling)
-   [23. Security and Privacy](#23-security-and-privacy)
-   [24. Testing Checklist](#24-testing-checklist)
-   [25. Troubleshooting](#25-troubleshooting)
-   [26. Accessibility and Responsive
    Design](#26-accessibility-and-responsive-design)
-   [27. Known Limitations and Verification
    Notes](#27-known-limitations-and-verification-notes)
-   [28. Future Enhancements](#28-future-enhancements)
-   [29. Contributing](#29-contributing)
-   [30. Git Workflow](#30-git-workflow)
-   [31. Frequently Asked Questions](#31-frequently-asked-questions)
-   [32. Project Summary](#32-project-summary)

------------------------------------------------------------------------

## 1. Project Overview

BookLoop is a campus-oriented marketplace for extending the useful life
of academic books. Instead of leaving textbooks unused after a semester,
students can make them available to other students through selling,
exchanging, or donating.

The application brings the book discovery and transaction-request
workflow into one place:

1.  A student signs in.
2.  The student browses books or publishes a listing.
3.  Another student opens a listing and sends an offer or request.
4.  The listing owner reviews the offer and accepts or rejects it.
5.  The students coordinate the handover outside the platform unless a
    dedicated coordination feature is implemented.

### Project at a glance

  -----------------------------------------------------------------------
  Item                                Description
  ----------------------------------- -----------------------------------
  Project name                        BookLoop

  Category                            Campus marketplace / student
                                      utility

  Primary users                       Students who want to reuse academic
                                      books

  Main purpose                        Discover, sell, exchange, or donate
                                      used books

  Frontend                            HTML5, CSS3, JavaScript

  Backend                             Python with Flask

  Database                            MySQL (verify the current local
                                      configuration)

  Local entry point                   `run.py`

  Backend application                 `backend/app.py`

  Database schema / seed file         `backend/schema.sql`

  Local development URL               Commonly `http://127.0.0.1:5000`
                                      when configured for port 5000
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 2. Problem Statement

Academic books can be expensive, and many remain unused after a course
or semester ends. Students who need those books may not know who has a
copy, while students who own them may struggle to find interested buyers
or recipients.

Common pain points include:

-   Difficulty finding relevant books within a campus community.
-   Limited visibility into book condition, price, or availability.
-   Informal buying and selling through scattered messages or groups.
-   No single place to manage offers and saved books.
-   Useful books being discarded or left unused instead of reused.

BookLoop addresses these problems with a shared listing and offer
workflow.

------------------------------------------------------------------------

## 3. Goals and Scope

### Primary goals

-   Make available academic books discoverable through a central
    interface.
-   Allow students to list books for sale, exchange, or donation.
-   Support offer submission and owner decisions.
-   Help users organize saved books and marketplace activity.
-   Provide a clear, understandable interface for student users.
-   Encourage reuse and reduce unnecessary book waste.

### In scope

-   Account registration and login, where implemented.
-   Book browsing and details.
-   Creating and managing listings.
-   Search and filtering, according to implemented UI behavior.
-   Offer creation and review.
-   Wishlist functionality.
-   Dashboard and profile pages.
-   Book and offer status tracking.

### Out of scope unless separately implemented

-   Integrated payments or escrow.
-   Automatic campus identity verification.
-   Built-in chat or real-time messaging.
-   Delivery or shipping management.
-   Automated dispute resolution.
-   Guaranteed real-time notifications.
-   A production deployment or high-availability infrastructure.

------------------------------------------------------------------------

## 4. Core Features

### 4.1 Authentication

Users can access account-related features through the login interface.
If registration and session-based authentication are enabled in the
current backend, protected actions should be available only to
authenticated users.

Expected responsibilities:

-   Register or sign in.
-   Identify the currently authenticated user.
-   Keep private account actions separate from public browsing.
-   Sign out and invalidate the relevant session.

### 4.2 Explore books

The Explore page is the discovery surface for the marketplace. It should
display book listings and provide a way to open a selected book.

Listing information may include:

-   Title and author.
-   Category or subject.
-   Condition.
-   Listing type (sell, exchange, or donate).
-   Price, where applicable.
-   Availability status.
-   Seller information and book image, where implemented.

### 4.3 Book details

A book details view provides more context than a listing card. It is the
place to review the book and decide whether to contact the owner through
an offer or other supported action.

### 4.4 Sell or publish a listing

The Sell page is used to create a listing. Depending on the implemented
form, a listing can contain descriptive information, condition,
transaction type, price, and image.

The backend should validate submitted values before writing them to the
database.

### 4.5 Offers

Offers connect interested students with listing owners. The offer
workflow should support:

-   Creating an offer for a book.
-   Viewing incoming and outgoing offers.
-   Accepting or rejecting an offer as the listing owner.
-   Displaying the current offer status.

### 4.6 Wishlist

The Wishlist page lets a user save books for later review. A wishlist
should be scoped to the current user so that one user cannot see or
modify another user's saved items.

### 4.7 Dashboard

The Dashboard provides a consolidated view of a user's marketplace
activity. Depending on the current implementation, this may include
their listings, offers, and book statuses.

### 4.8 Profile

The Profile page provides the user's account details and, if supported,
profile-editing actions.

### 4.9 Exchange and donation

BookLoop's intended marketplace supports more than direct sales:

-   **Sell:** a seller lists a book with a price.
-   **Exchange:** students arrange a book-for-book exchange.
-   **Donate:** a student offers a book without charging a sale price.

The exact form fields and transaction rules should match the current
implementation.

------------------------------------------------------------------------

## 5. Technology Stack

  -----------------------------------------------------------------------
  Technology                          Role
  ----------------------------------- -----------------------------------
  HTML5                               Page structure and semantic content

  CSS3                                Layout, visual design, responsive
                                      styling

  JavaScript                          Client-side interactions and API
                                      communication

  Python                              Backend application logic

  Flask                               HTTP routes and API handling

  MySQL                               Persistent relational data storage

  `mysql-connector-python`            Python-to-MySQL connectivity, if
                                      used by the current backend

  `flask-cors`                        Cross-origin request handling, if
                                      configured

  Git and GitHub                      Source control and repository
                                      hosting

  VS Code                             Suggested development editor
  -----------------------------------------------------------------------

The actual dependencies should be verified from the project's dependency
file, if present, or from the imports in `backend/app.py`.

------------------------------------------------------------------------

## 6. Repository Structure

The current top-level project structure includes the following files and
folders:

``` text
bookloop/
├── backend/
│   ├── app.py                 # Flask application and backend routes (expected)
│   └── schema.sql             # Database schema / seed script (expected)
├── css/
│   └── ...                    # Stylesheets
├── images/
│   └── ...                    # Book and interface images
├── js/
│   ├── app.js                 # Shared client-side behavior (expected)
│   └── ...                    # Page-specific JavaScript, if present
├── index.html                 # Landing / entry page
├── login.html                 # Login interface
├── explore.html               # Browse book listings
├── book.html                  # Book details
├── sell.html                  # Create a listing
├── offers.html                # Offer management
├── wishlist.html              # Saved books
├── dashboard.html             # User activity overview
├── profile.html               # User profile
├── wanted.html                # Wanted-book page / request interface (verify behavior)
├── run.py                     # Local launcher
├── start_server.bat           # Windows startup helper
├── .gitignore                 # Files excluded from Git
└── README.md                  # Project documentation
```

> The listing above describes the known top-level files. Run
> `Get-ChildItem -Recurse` in PowerShell to inspect the exact contents
> of `backend/`, `css/`, `images/`, and `js/`. Update this tree to match
> the committed repository.

------------------------------------------------------------------------

## 7. System Architecture

### 7.1 High-level architecture

``` mermaid
flowchart TB
    U[Student / User]
    subgraph Client["Client Layer"]
        P[HTML Pages]
        C[CSS Stylesheets]
        J[JavaScript]
    end
    subgraph Server["Application Layer"]
        R[Flask Routes / API]
        V[Validation and Business Rules]
        A[Authentication and Session Checks]
    end
    subgraph Data["Data Layer"]
        DB[(MySQL Database)]
    end

    U --> P
    P --- C
    P --> J
    J -->|HTTP requests| R
    R --> A
    A --> V
    V -->|SQL queries| DB
    DB --> V
    V --> R
    R -->|JSON / HTTP response| J
    J --> P
```

**How it works:** the browser renders the HTML and CSS. JavaScript
handles interactions and, where configured, sends HTTP requests to
Flask. Flask validates the request, applies business rules, interacts
with MySQL, and returns an HTTP response or JSON payload.

### 7.2 Layer responsibilities

  -----------------------------------------------------------------------
  Layer                   Responsibility          Examples
  ----------------------- ----------------------- -----------------------
  Presentation            Render pages and forms  `explore.html`,
                                                  `sell.html`

  Client logic            Form behavior and API   files in `js/`
                          calls                   

  API / routing           Receive and dispatch    `backend/app.py`
                          requests                

  Business logic          Apply marketplace rules Offer and listing
                                                  validation

  Persistence             Store and retrieve      MySQL tables
                          records                 

  Startup                 Start the local         `run.py`,
                          application             `start_server.bat`
  -----------------------------------------------------------------------

### 7.3 Deployment view

``` mermaid
flowchart LR
    B[Browser on developer / student device]
    APP[BookLoop Flask process]
    SQL[(MySQL service)]

    B -->|HTTP on configured host and port| APP
    APP -->|Database connection| SQL
```

For local development, these services may run on the same computer. A
public deployment would need separate configuration for hosting,
database access, HTTPS, secrets, and production server settings.

------------------------------------------------------------------------

## 8. Application Modules

``` mermaid
flowchart TD
    ROOT[BookLoop]
    ROOT --> AUTH[Authentication]
    ROOT --> DISC[Book Discovery]
    ROOT --> LIST[Listing Management]
    ROOT --> OFF[Offer Management]
    ROOT --> WISH[Wishlist]
    ROOT --> DASH[Dashboard]
    ROOT --> PROF[Profile]
    ROOT --> WANTED[Wanted Books]
    ROOT --> DATA[Database / Persistence]
    AUTH --> DATA
    DISC --> DATA
    LIST --> DATA
    OFF --> DATA
    WISH --> DATA
    DASH --> DATA
    PROF --> DATA
    WANTED --> DATA
```

### Module responsibility matrix

  -----------------------------------------------------------------------
  Module                  Primary page(s)         Responsibility
  ----------------------- ----------------------- -----------------------
  Authentication          `login.html`            Sign-in and account
                                                  access

  Book discovery          `explore.html`          Browse and find books

  Book detail             `book.html`             Display an individual
                                                  listing

  Listing management      `sell.html`             Publish book details
                                                  and transaction type

  Offer management        `offers.html`           Review and respond to
                                                  offers

  Wishlist                `wishlist.html`         Save and revisit books

  Dashboard               `dashboard.html`        Summarize user activity

  Profile                 `profile.html`          Display and manage user
                                                  details

  Wanted books            `wanted.html`           Support wanted-book
                                                  functionality, if
                                                  implemented

  Backend                 `backend/app.py`        Handle application
                                                  requests

  Database                `backend/schema.sql`    Define schema and
                                                  potentially seed
                                                  records
  -----------------------------------------------------------------------

### 8.1 Authentication module

**Inputs:** account credentials and authentication actions.

**Responsibilities:**

-   Validate required fields.
-   Verify credentials securely.
-   Establish a session on successful authentication.
-   Return a meaningful error for invalid credentials.
-   Protect endpoints that require authentication.

**Important:** passwords should be stored as salted password hashes,
never as plain text.

### 8.2 Discovery module

**Inputs:** optional search terms, filters, sorting, or selected listing
identifiers.

**Responsibilities:**

-   Retrieve eligible listings.
-   Return data needed by the listing cards.
-   Expose details for a selected listing.
-   Handle empty search results and unavailable books.

### 8.3 Listing module

**Inputs:** book metadata and the selected transaction type.

**Responsibilities:**

-   Validate listing details.
-   Associate the listing with its owner.
-   Set an initial status.
-   Return a success or failure result.
-   Prevent users from changing listings they do not own.

### 8.4 Offer module

**Inputs:** book identifier, offer information, and owner decision.

**Responsibilities:**

-   Confirm that the target book exists and is eligible.
-   Associate the offer with the buyer and the book.
-   Track pending, accepted, or rejected status.
-   Authorize acceptance or rejection by the listing owner.
-   Keep the book and related offers consistent when an offer is
    accepted.

### 8.5 Wishlist module

**Inputs:** user identifier and book identifier.

**Responsibilities:**

-   Add a book to a user's saved list.
-   Remove a saved book.
-   Retrieve the current user's wishlist.
-   Avoid duplicate saves if the data model enforces uniqueness.

### 8.6 Dashboard module

**Responsibilities:**

-   Summarize a user's listings.
-   Show offer activity.
-   Display statuses and useful counts.
-   Handle users who have no activity yet.

### 8.7 Profile module

**Responsibilities:**

-   Retrieve the authenticated user's profile.
-   Validate permitted profile updates.
-   Avoid allowing users to modify protected fields belonging to other
    users.

### 8.8 Wanted-book module

The top-level repository contains `wanted.html`. Inspect its JavaScript
and backend integration to determine whether it supports a request form,
a list of wanted books, or another feature. Document only the behavior
actually implemented.

------------------------------------------------------------------------

## 9. User Roles and Permissions

The known product is student-focused. Unless a separate administrator
role is implemented, the main role is a registered user who can act as
both a buyer and a seller.

  -----------------------------------------------------------------------
  Action                    Visitor Authenticated user      Listing owner
  -------------- ------------------ ------------------ ------------------
  View public            If enabled                Yes                Yes
  listings                                             

  Create a                       No                Yes                Yes
  listing                                              

  Submit an                      No                Yes    Yes, subject to
  offer                                                  self-offer rules

  View own                       No                Yes                Yes
  offers                                               

  Accept /                       No   No, unless owner Yes, for their own
  reject an                                                       listing
  offer                                                

  Manage own                     No                Yes                Yes
  wishlist                                             

  Manage own                     No                Yes                Yes
  profile                                              

  Edit another                   No                 No                 No
  user's listing                                       
  -----------------------------------------------------------------------

This table is a recommended authorization model; verify each row against
the live implementation. A disabled button in the browser is not a
security boundary. The backend must enforce permissions too.

------------------------------------------------------------------------

## 10. Main User Journeys

### 10.1 Browse and make an offer

``` mermaid
flowchart TD
    S([Start]) --> E[Open Explore]
    E --> Q[Search or browse listings]
    Q --> D[Open a book]
    D --> A{Book available?}
    A -- No --> N[Show current status]
    A -- Yes --> L{Signed in?}
    L -- No --> LOGIN[Sign in]
    LOGIN --> O[Submit offer]
    L -- Yes --> O
    O --> V[Validate offer on server]
    V --> P[Create pending offer]
    P --> DONE[Show confirmation]
    N --> END([End])
    DONE --> END
```

### 10.2 Publish a book

``` mermaid
flowchart TD
    S([Start]) --> LOGIN[Sign in]
    LOGIN --> SELL[Open Sell page]
    SELL --> FORM[Enter book details]
    FORM --> VALID{Form valid?}
    VALID -- No --> ERR[Show validation errors]
    ERR --> FORM
    VALID -- Yes --> API[Submit listing]
    API --> SERVER[Server validates fields and user]
    SERVER --> SAVE[(Save listing)]
    SAVE --> RESULT[Show success and listing]
    RESULT --> END([End])
```

### 10.3 Review an incoming offer

``` mermaid
flowchart TD
    S([Seller opens Offers]) --> P[Load incoming pending offers]
    P --> DEC{Seller decision}
    DEC -- Reject --> R[Mark offer rejected]
    DEC -- Accept --> CHECK[Recheck book and offer state]
    CHECK --> OK{Still eligible?}
    OK -- No --> FAIL[Return conflict / updated status]
    OK -- Yes --> A[Accept selected offer]
    A --> BOOK[Update book status as designed]
    BOOK --> OTHERS[Resolve competing pending offers]
    OTHERS --> CONF[Return confirmation]
    R --> CONF
    FAIL --> END([Refresh and review])
    CONF --> END2([End])
```

### 10.4 Wishlist workflow

``` mermaid
flowchart LR
    B[Explore a book] --> ACT[Choose Save to Wishlist]
    ACT --> AUTH{Authenticated?}
    AUTH -- No --> SIGN[Ask user to sign in]
    AUTH -- Yes --> SAVE[Save user-book association]
    SAVE --> VIEW[Open Wishlist]
    VIEW --> REMOVE[Optional: remove saved book]
```

------------------------------------------------------------------------

## 11. Book and Offer Lifecycles

### 11.1 Book lifecycle

The previously documented status model is:

``` mermaid
stateDiagram-v2
    [*] --> AVAILABLE: Listing published
    AVAILABLE --> RESERVED: Offer accepted / reservation created
    RESERVED --> SOLD: Sale or handover completed
    RESERVED --> AVAILABLE: Reservation cancelled, if supported
    AVAILABLE --> [*]: Listing removed, if supported
    SOLD --> [*]
```

The transitions supported by the application must be verified. In
particular, exchange and donation may require different completion
labels than a cash sale.

### 11.2 Offer lifecycle

``` mermaid
stateDiagram-v2
    [*] --> PENDING: Offer submitted
    PENDING --> ACCEPTED: Owner accepts
    PENDING --> REJECTED: Owner rejects
    ACCEPTED --> [*]
    REJECTED --> [*]
```

### 11.3 Consistency rules

When an offer is accepted, the server should apply the related changes
as one database transaction where possible:

1.  Confirm the current user owns the listing.
2.  Confirm the book is still eligible for an offer.
3.  Confirm the offer is still pending.
4.  Accept the selected offer.
5.  Update the book status according to the intended workflow.
6.  Reject or otherwise resolve competing pending offers according to
    the product rules.
7.  Commit all changes together.

If any operation fails, roll back the transaction so that the database
does not end up with an accepted offer but an unchanged book status, or
the reverse.

------------------------------------------------------------------------

## 12. Data Model

The documented data model includes four core entities: `users`, `books`,
`offers`, and `wishlists`. The exact column names and constraints must
be taken from `backend/schema.sql`.

### 12.1 Entity descriptions

**Users**

Represents student accounts. Typical fields include a primary key,
display name, email, password hash, and timestamps. These are conceptual
examples; use the actual schema for exact names.

**Books**

Represents marketplace listings. A record is associated with its owner
and contains descriptive information, transaction type, price where
relevant, and status.

**Offers**

Represents a user's interest in a listed book. Each offer is associated
with a book, a buyer, and a status. The documented relationship includes
`offers.buyer_id` referencing `users.id`.

**Wishlists**

Represents saved-book relationships. A wishlist record associates a user
with a book. A unique constraint on `(user_id, book_id)` is recommended
to prevent duplicates.

### 12.2 Conceptual schema

``` mermaid
erDiagram
    USERS ||--o{ BOOKS : lists
    USERS ||--o{ OFFERS : submits
    BOOKS ||--o{ OFFERS : receives
    USERS ||--o{ WISHLISTS : owns
    BOOKS ||--o{ WISHLISTS : saved_in

    USERS {
        int id PK
        string name
        string email
        string password_hash
    }
    BOOKS {
        int id PK
        int owner_id FK
        string title
        string condition
        string listing_type
        decimal price
        string status
    }
    OFFERS {
        int id PK
        int book_id FK
        int buyer_id FK
        string status
    }
    WISHLISTS {
        int id PK
        int user_id FK
        int book_id FK
    }
```

**Important:** this ER diagram is conceptual, not a substitute for the
SQL schema. Column names, data types, nullability, foreign keys, and
additional fields may differ in the actual implementation. Adjust the
diagram after checking `backend/schema.sql`.

### 12.3 Database integrity recommendations

-   Use primary keys for all entities.
-   Use foreign keys for user-book, offer-book, offer-buyer, and
    wishlist relationships.
-   Store prices using a fixed-precision numeric type, not floating
    point.
-   Enforce uniqueness for account email addresses.
-   Consider uniqueness for wishlist user-book pairs.
-   Add indexes for frequently filtered fields such as book status,
    listing type, and foreign keys.
-   Use transactions for multi-step offer acceptance.
-   Decide deliberately whether deleting a user or book should cascade,
    restrict, or preserve historical records.

------------------------------------------------------------------------

## 13. Database Relationship Diagram

``` mermaid
flowchart TB
    U[(users)]
    B[(books)]
    O[(offers)]
    W[(wishlists)]

    U -->|owner / seller relationship| B
    U -->|buyer_id| O
    B -->|book_id| O
    U -->|user_id| W
    B -->|book_id| W
```

A user can publish multiple books, submit multiple offers, and save
multiple books. A book can receive multiple offers and be saved by
multiple users. The exact cardinality and delete rules should be checked
against the foreign keys in the schema.

------------------------------------------------------------------------

## 14. Request and Response Flow

### 14.1 Example: creating an offer

``` mermaid
sequenceDiagram
    actor Student
    participant Browser
    participant JS as Frontend JavaScript
    participant Flask as Flask Backend
    participant DB as MySQL

    Student->>Browser: Submit offer form
    Browser->>JS: Validate required input
    JS->>Flask: Send HTTP request
    Flask->>Flask: Authenticate and validate
    Flask->>DB: Check book and current status
    DB-->>Flask: Book record / status
    Flask->>DB: Insert pending offer
    DB-->>Flask: Insert result
    Flask-->>JS: HTTP response / JSON
    JS-->>Browser: Show success or error
    Browser-->>Student: Updated interface
```

### 14.2 Example: protected request

``` mermaid
flowchart TD
    REQ[Incoming request] --> SESSION{Valid session?}
    SESSION -- No --> UNAUTH[Return unauthorized response]
    SESSION -- Yes --> INPUT[Validate request data]
    INPUT --> VALID{Valid?}
    VALID -- No --> BAD[Return validation error]
    VALID -- Yes --> AUTHZ{User permitted?}
    AUTHZ -- No --> DENY[Return forbidden response]
    AUTHZ -- Yes --> LOGIC[Execute business logic]
    LOGIC --> RESP[Return result]
```

This flow is a recommended backend pattern. Match the response codes and
exact session implementation to `backend/app.py`.

------------------------------------------------------------------------

## 15. Local Installation

### 15.1 Prerequisites

Install or confirm the following:

-   Python 3.
-   MySQL Server compatible with the project's schema.
-   Git (optional for cloning and version control).
-   A modern web browser.
-   A terminal such as PowerShell or Windows Terminal.

Confirm Python:

``` powershell
python --version
```

Confirm Git:

``` powershell
git --version
```

Confirm MySQL is installed and available using your installation's MySQL
client or service manager.

### 15.2 Get the project

If cloning from GitHub:

``` powershell
git clone https://github.com/YOUR-USERNAME/BookLoop.git
cd BookLoop
```

Replace the URL with the actual repository URL.

If the project is already on your computer, open PowerShell in the
project root instead.

### 15.3 Create a virtual environment

From the project root:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation due to execution policy, use a permitted
environment-specific workaround or run the Python executable inside
`.venv` directly. Avoid changing machine-wide security policy
unnecessarily.

### 15.4 Install dependencies

If a `requirements.txt` exists:

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If no dependency file exists, inspect the imports in `backend/app.py`
and install only the required packages. The previously documented stack
may use:

``` powershell
pip install Flask flask-cors mysql-connector-python
```

Do not install this list blindly if the project uses different packages
or versions. Once dependencies are confirmed, create a reproducible
`requirements.txt`.

------------------------------------------------------------------------

## 16. Configuration

### 16.1 Database settings

The Flask application needs a database connection configuration. Inspect
`backend/app.py` to determine whether it reads environment variables, a
configuration file, or values defined in code.

Recommended configuration variables:

``` text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bookloop
DB_USER=your_local_database_user
DB_PASSWORD=your_local_database_password
```

These are suggested names, not a claim that the current application
already reads them.

### 16.2 Keep secrets out of Git

-   Do not commit database passwords.
-   Do not commit production credentials or API keys.
-   Do not commit private database dumps or real student data.
-   Use local environment variables or a local `.env` file if supported
    by the application.
-   Provide an `.env.example` containing placeholder values only if the
    application uses environment-based configuration.

Example placeholder file:

``` dotenv
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bookloop
DB_USER=your_username
DB_PASSWORD=replace_me
```

Do not place real credentials in the example file. A `.gitignore` entry
prevents future tracking of untracked files but does not remove a secret
that has already been committed.

------------------------------------------------------------------------

## 17. Database Setup

### 17.1 Create the database

Connect to MySQL using your configured local account. For example:

``` sql
CREATE DATABASE bookloop;
```

Then select the database:

``` sql
USE bookloop;
```

### 17.2 Apply the schema

If `backend/schema.sql` contains the table definitions and seed data,
run it using a MySQL client. From PowerShell, a common pattern is:

``` powershell
mysql -u YOUR_DB_USER -p bookloop < .\backend\schema.sql
```

Replace `YOUR_DB_USER` with your local MySQL username. The command
assumes the `mysql` client is available on `PATH`; otherwise use the
full path to `mysql.exe` or run the SQL file through MySQL Workbench.

If the schema file itself creates the database, follow its instructions
and avoid creating duplicate objects.

### 17.3 Seed data and foreign keys

Create parent records before dependent records. For example, if sample
books reference users, create the demo users first; offers should
reference existing users and books. This avoids foreign-key errors.

Use fake/demo data only. Never seed public repositories with real
passwords, contact details, or private user records.

### 17.4 Verify tables

After importing the schema, run:

``` sql
SHOW TABLES;
```

Inspect table definitions with:

``` sql
DESCRIBE users;
DESCRIBE books;
DESCRIBE offers;
DESCRIBE wishlists;
```

Run only the commands for tables that exist in the actual schema.

------------------------------------------------------------------------

## 18. Running BookLoop

### Option A: Use the Python launcher

From the root folder:

``` powershell
python run.py
```

The launcher is expected to start the application, but inspect `run.py`
if it reports a missing module, incorrect working directory, or port
conflict.

### Option B: Use the Windows batch file

``` powershell
.\start_server.bat
```

Use this option if the batch file is configured for your current Python
environment and project paths.

### Option C: Start Flask directly

If `backend/app.py` exposes the Flask application and supports direct
execution, follow its documented launch command. Do not assume a
particular module name or startup flag without checking the file.

### Open the application

If the server starts on port 5000, open:

``` text
http://127.0.0.1:5000
```

The exact URL depends on the host and port configured in `run.py` or
`backend/app.py`.

### Startup checklist

-   [ ] Python starts without import errors.
-   [ ] MySQL service is running.
-   [ ] Database and required tables exist.
-   [ ] Backend connects to MySQL successfully.
-   [ ] The terminal shows the expected host and port.
-   [ ] The landing page opens.
-   [ ] Browser requests do not fail due to incorrect API paths.
-   [ ] Authentication and protected actions behave as expected.

------------------------------------------------------------------------

## 19. Application Pages

  -----------------------------------------------------------------------
  File                    Intended purpose        Key checks
  ----------------------- ----------------------- -----------------------
  `index.html`            Landing / entry page    Navigation and calls to
                                                  action work

  `login.html`            Login                   Validation and clear
                                                  authentication errors

  `explore.html`          Browse books            Listings load and
                                                  filters behave
                                                  correctly

  `book.html`             Book details            Correct selected book
                                                  is displayed

  `sell.html`             Publish a listing       Required fields and
                                                  transaction type are
                                                  validated

  `offers.html`           Offers                  Incoming/outgoing
                                                  offers and decisions
                                                  are accurate

  `wishlist.html`         Saved books             Only the current user's
                                                  saved items are shown

  `dashboard.html`        Activity summary        Counts and listing
                                                  states are consistent

  `profile.html`          User profile            Profile data is loaded
                                                  and updates are
                                                  authorized

  `wanted.html`           Wanted books            Verify actual
                                                  request/list behavior
  -----------------------------------------------------------------------

### Navigation map

``` mermaid
flowchart TD
    HOME[index.html]
    LOGIN[login.html]
    EXPLORE[explore.html]
    BOOK[book.html]
    SELL[sell.html]
    OFFERS[offers.html]
    WISH[wishlist.html]
    DASH[dashboard.html]
    PROFILE[profile.html]
    WANTED[wanted.html]

    HOME --> LOGIN
    HOME --> EXPLORE
    EXPLORE --> BOOK
    BOOK --> LOGIN
    LOGIN --> DASH
    DASH --> SELL
    DASH --> OFFERS
    DASH --> WISH
    DASH --> PROFILE
    EXPLORE --> WANTED
```

This is a conceptual navigation map. Verify actual links and redirects
in the HTML and JavaScript.

------------------------------------------------------------------------

## 20. API Documentation Guide

The backend is expected to define HTTP routes in `backend/app.py`.
Document the exact paths and methods from the code rather than assuming
that a route exists.

### Recommended endpoint inventory

  Domain           Operations to document
  ---------------- -----------------------------------------------------
  Authentication   Register, login, current user, logout
  Books            List, details, create, update, delete or deactivate
  Offers           Create, list incoming/outgoing, accept, reject
  Wishlist         List, add, remove
  Dashboard        Retrieve current user's activity summary
  Profile          Retrieve and update current user's profile
  Wanted books     Create and browse requests, if implemented

### Endpoint documentation template

For every actual route, record:

-   **Method and path:** for example, `GET /api/...`
-   **Purpose:** what the route does.
-   **Authentication:** public or authenticated.
-   **Request parameters:** path, query, and body fields.
-   **Validation:** required values and constraints.
-   **Success response:** actual status code and JSON shape.
-   **Failure responses:** validation, authentication, permission,
    missing record, and server errors.
-   **Side effects:** database changes and related status transitions.

### Example request-flow contract

A JSON request might look like this, depending on the implemented offer
API:

``` json
{
  "book_id": 123,
  "message": "I am interested in this book."
}
```

This is an illustrative payload only. Replace the fields and endpoint
with those actually supported by the backend.

### API verification

Inspect the Flask route declarations and test them using the browser's
developer tools, a REST client, or command-line HTTP tooling. Keep API
documentation synchronized with the implementation.

------------------------------------------------------------------------

## 21. Validation and Business Rules

The following rules are recommended for a consistent marketplace.
Confirm which ones are already enforced.

### Account rules

-   Required fields must not be empty.
-   Email addresses should be normalized and unique.
-   Passwords must be hashed using a suitable password-hashing method.
-   Authentication errors should not disclose sensitive account details.
-   Protected routes must validate the server-side session.

### Listing rules

-   A listing must have an existing owner.
-   Required descriptive fields must be validated on the server.
-   Price must be valid and non-negative for sale listings.
-   Exchange and donation listings should not require a sale price
    unless the design explicitly says otherwise.
-   A user should not edit or remove a listing owned by someone else.
-   Unavailable listings should not accept new offers.

### Offer rules

-   An offer must reference an existing book and buyer.
-   The buyer should not be allowed to offer on their own listing unless
    self-offers are deliberately supported.
-   Only the listing owner can accept or reject an offer.
-   Only pending offers should be eligible for a decision.
-   Acceptance should re-check the book status to avoid stale or
    conflicting requests.
-   Concurrent acceptance requests should not produce multiple accepted
    outcomes for one listing if the product intends only one active
    reservation.

### Wishlist rules

-   Only the authenticated user can modify their wishlist.
-   A book should not appear multiple times for the same user if
    duplicates are not intended.
-   Removing an item should not delete the book itself.

------------------------------------------------------------------------

## 22. Error Handling

A robust interface should communicate failures in a way the user can act
on.

  Situation                  Expected behavior
  -------------------------- ----------------------------------------------
  Invalid form fields        Show field-level validation messages
  Incorrect credentials      Show a generic sign-in error
  Session expired            Ask the user to sign in again
  Listing not found          Show a not-found state
  Book no longer available   Explain that the status has changed
  Unauthorized action        Reject the request on the server
  Database unavailable       Show a safe error and log diagnostic details
  Network failure            Offer a retry where appropriate
  Empty results              Show an informative empty state

Avoid displaying database credentials, SQL statements, stack traces, or
internal filesystem paths to end users. Detailed diagnostics belong in
protected development logs.

------------------------------------------------------------------------

## 23. Security and Privacy

BookLoop involves user accounts and interactions between students, so
server-side checks matter even for a student project.

### Authentication and sessions

-   Hash passwords with a modern password-hashing function.
-   Use secure session configuration.
-   In production, enable HTTPS and appropriate cookie flags such as
    `Secure`, `HttpOnly`, and a suitable `SameSite` policy.
-   Set session expiry and logout behavior deliberately.
-   Protect state-changing actions against cross-site request forgery
    when cookie-based authentication is used.

### SQL safety

-   Use parameterized SQL queries.
-   Never build SQL by concatenating untrusted form values.
-   Validate identifiers and values on the server.
-   Use a database account with only the permissions the application
    needs.

### Authorization

-   Verify ownership before editing, deleting, accepting, or rejecting a
    listing-related record.
-   Do not trust user IDs supplied by the browser; derive the
    authenticated user's identity from the server-side session.
-   Apply the same permission checks to API requests as to UI actions.

### Input and output safety

-   Validate user-submitted text and numeric values.
-   Escape user-generated content when rendering it into HTML.
-   Restrict accepted image types and sizes if uploads are supported.
-   Avoid serving arbitrary filesystem paths from user input.

### Secrets and repository hygiene

-   Keep `.env`, database dumps, personal records, and credentials out
    of Git.
-   Use demo data for screenshots and examples.
-   Rotate any credential that was accidentally committed; deleting it
    from the latest version alone does not erase it from Git history.

### Production readiness

A local development server is not a production deployment. Before public
deployment, review debug mode, secret management, database exposure,
HTTPS, session cookies, logging, backups, rate limiting, dependency
versions, and deployment server configuration.

------------------------------------------------------------------------

## 24. Testing Checklist

### Authentication

-   [ ] Valid credentials sign in successfully.
-   [ ] Invalid credentials produce a safe error.
-   [ ] Protected actions reject unauthenticated requests.
-   [ ] Logout ends the active session.
-   [ ] A user cannot access another user's private data.

### Listings

-   [ ] A valid listing can be created.
-   [ ] Missing required fields are rejected.
-   [ ] Invalid prices are rejected.
-   [ ] Listings display the correct transaction type and status.
-   [ ] Users cannot edit another user's listing.
-   [ ] Unavailable books cannot receive new offers.

### Offers

-   [ ] A valid offer can be submitted.
-   [ ] An offer appears for the appropriate participants.
-   [ ] The listing owner can accept or reject an eligible offer.
-   [ ] A non-owner cannot decide an offer.
-   [ ] A resolved offer cannot be resolved again.
-   [ ] Competing offers are handled consistently.
-   [ ] Concurrent requests do not leave inconsistent records.

### Wishlist

-   [ ] A book can be saved.
-   [ ] A saved book appears in the correct user's wishlist.
-   [ ] Duplicate saves are handled correctly.
-   [ ] A saved book can be removed.
-   [ ] One user cannot alter another user's wishlist.

### User interface

-   [ ] Navigation links work.
-   [ ] Empty states are understandable.
-   [ ] Loading and error states are handled.
-   [ ] Forms work with keyboard input.
-   [ ] Layout remains usable on mobile and desktop.
-   [ ] Images have useful alternative text where appropriate.

### Database

-   [ ] Foreign keys are valid.
-   [ ] Duplicate account emails are rejected.
-   [ ] Failed multi-step transactions roll back cleanly.
-   [ ] Demo seed data uses valid parent-child relationships.
-   [ ] Database connection failures do not expose secrets.

------------------------------------------------------------------------

## 25. Troubleshooting

### Flask does not start

1.  Activate the intended Python environment.
2.  Check the terminal for the first traceback.
3.  Install the missing dependency if it is genuinely required.
4.  Confirm `run.py` points to the correct backend module.
5.  Check whether the configured port is already in use.

### MySQL connection fails

1.  Confirm the MySQL service is running.
2.  Verify the host, port, database name, username, and password.
3.  Confirm the database exists.
4.  Confirm the database user has the required permissions.
5.  Check that the schema was imported successfully.
6.  Do not paste real database passwords into public issue reports.

### `mysql` is not recognized

The MySQL client may not be on the Windows `PATH`. Use MySQL Workbench,
add the correct MySQL `bin` directory to the user `PATH`, or invoke
`mysql.exe` with its full path. Restart the terminal after changing
environment variables.

### Page loads but data is missing

1.  Check whether the backend process is still running.
2.  Inspect the browser console and Network tab.
3.  Verify the frontend's API URL and route.
4.  Inspect the backend terminal logs.
5.  Confirm the expected database tables contain data.
6.  Check whether the API response format matches what the JavaScript
    expects.

### Foreign-key error during seeding

Insert parent records first. For example, create users before books
owned by those users, then create offers that reference existing users
and books.

### Git accidentally stages a private file

Before committing, inspect:

``` powershell
git status
git diff --cached --stat
git diff --cached
```

Unstage a file with:

``` powershell
git restore --staged path\to\file
```

Then add the correct ignore rule. If a secret has already been committed
or pushed, revoke or rotate it immediately and clean the repository
history as appropriate.

------------------------------------------------------------------------

## 26. Accessibility and Responsive Design

A student marketplace should be usable across common screen sizes and
input methods.

Recommended checks:

-   Use semantic HTML landmarks and meaningful headings.
-   Associate form labels with their inputs.
-   Ensure keyboard focus is visible.
-   Provide text labels for icon-only controls.
-   Use sufficient text and control contrast.
-   Include meaningful `alt` text for informative book images.
-   Avoid communicating status through color alone.
-   Make buttons and links large enough to use comfortably on
    touchscreens.
-   Test narrow mobile widths, tablet layouts, and desktop layouts.
-   Ensure errors are announced and associated with the relevant form
    fields where practical.

These are recommended quality criteria; verify the current
implementation before claiming complete accessibility conformance.

------------------------------------------------------------------------

## 27. Known Limitations and Verification Notes

This section should be updated after testing the current source code.

-   The exact route list and API payloads need to be confirmed from
    `backend/app.py`.
-   The exact table columns, constraints, and seed records need to be
    confirmed from `backend/schema.sql`.
-   The exact dependency versions should be recorded in a dependency
    file.
-   The behavior of `wanted.html` should be checked against its
    JavaScript and backend route.
-   The final meaning of `RESERVED`, `SOLD`, and completion actions
    should match the code and interface.
-   Integrated payment, chat, delivery, notifications, and dispute
    handling should not be advertised unless implemented.
-   Deployment and production security should be documented only after
    the deployment environment has been configured and tested.

------------------------------------------------------------------------

## 28. Future Enhancements

Potential extensions, in priority order:

### Marketplace experience

-   Advanced search by title, author, subject, condition, price, and
    listing type.
-   Sorting by newest, price, or relevance.
-   Better listing photos and image validation.
-   Pagination for large result sets.
-   Clear empty, loading, and unavailable states.

### Student trust and coordination

-   Verified college email, if appropriate for the intended campus.
-   In-app messaging between interested students.
-   Handover scheduling and location coordination.
-   Reporting and moderation workflows.
-   Ratings or feedback after a completed exchange, with anti-abuse
    protections.

### Transaction workflow

-   Explicit completion or cancellation action for reserved listings.
-   Clear exchange-specific and donation-specific lifecycle states.
-   Notifications when offers are received or resolved.
-   Concurrency-safe offer acceptance.
-   A history of listing and offer state changes.

### Engineering improvements

-   Automated unit and integration tests.
-   A documented API contract.
-   Centralized configuration and secret management.
-   Database migrations.
-   Structured logging and safer error responses.
-   CI checks for tests, formatting, and dependency vulnerabilities.
-   A production deployment with HTTPS and managed database backups.

### Analytics

-   Most requested subjects or book categories.
-   Listing-to-offer conversion.
-   Number of books reused or donated.
-   Average time for a listing to receive an offer.

Collect only data that is necessary, disclose its use, and avoid
exposing personal information in public analytics.

------------------------------------------------------------------------

## 29. Contributing

Contributions should keep the application understandable, secure, and
consistent with its existing structure.

1.  Create a branch for the change.
2.  Keep changes focused and descriptive.
3.  Test the affected page and backend route.
4.  Do not include credentials, personal records, or unrelated local
    files.
5.  Update this README if a feature, setup step, or data model changes.
6.  Submit a pull request with a summary and test notes.

Suggested branch names:

``` text
feature/book-search
feature/offer-validation
fix/wishlist-duplicate
docs/update-readme
```

------------------------------------------------------------------------

## 30. Git Workflow

### Initial push

If the local project has not yet been pushed to GitHub:

``` powershell
git init -b main
git add .
git status
git commit -m "Initial commit - BookLoop project"
git remote add origin https://github.com/YOUR-USERNAME/BookLoop.git
git push -u origin main
```

If Git has already been initialized and the remote configured, do not
repeat `git init` or `git remote add origin`. Check the current state
first:

``` powershell
git status
git remote -v
git branch
```

### Publish README updates

After saving changes to `README.md`:

``` powershell
git add README.md
git commit -m "docs: add detailed BookLoop documentation"
git push
```

Before pushing, review staged changes and confirm no secrets, local
database files, or private data are included.

------------------------------------------------------------------------

## 31. Frequently Asked Questions

### What problem does BookLoop solve?

It helps students find and reuse academic books through a central
listing and offer workflow.

### Can a student donate a book instead of selling it?

Donation is part of the intended product scope. Verify the current
listing form and backend rules to confirm how donation listings are
represented.

### What happens when an offer is accepted?

The intended workflow marks the offer as accepted and updates the book's
state according to the application's transaction rules. Confirm the
exact state transition in the backend.

### Does BookLoop process payments?

Do not assume that it does. Payment processing is outside the documented
core scope unless a payment integration has been implemented separately.

### Where is the database schema?

The known schema file is `backend/schema.sql`.

### How is the application started?

The project includes `run.py` and `start_server.bat`. The normal local
entry point is expected to be `python run.py`, subject to the actual
launcher configuration.

### Can I deploy this publicly?

Potentially, but first review authentication, authorization, secrets,
HTTPS, production server settings, database access, error handling, and
privacy. A successful local run does not by itself mean the application
is production-ready.

------------------------------------------------------------------------

## 32. Project Summary

BookLoop is a student-focused academic book reuse marketplace with a web
frontend, a Python/Flask backend, and a relational database. Its core
workflow brings together book discovery, listing publication, offers,
wishlists, and user activity.

The project's value is practical: it makes useful books easier to find
and gives students a structured way to sell, exchange, or donate them.
The next steps for a polished project release are to verify every README
detail against the source code, add repeatable setup instructions, test
key workflows, and keep credentials and private data out of the public
repository.

------------------------------------------------------------------------
