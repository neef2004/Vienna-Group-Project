# AI Use in the Frontend Development Process

## Overview

Generative AI was used as a supporting tool during the development of the
Itinerary App. It helped the development team understand problems, explore
possible solutions, draft parts of the implementation, and improve project
documentation. AI did not build or manage the project independently. The team
made the design decisions, selected which suggestions to use, adapted them to
the codebase, and remained responsible for the final result.

## How AI Was Used

### 1. Planning and problem solving

AI was used to discuss possible ways to divide the application into a React and
TypeScript frontend and a Flask backend. It also helped break larger tasks into
smaller implementation steps and suggested approaches for features such as
authentication, trip management, itineraries, reminders, collaborators, and
calendar display.

These suggestions were used for brainstorming. The team decided which approach
matched the project requirements and existing architecture.

### 2. Code assistance

AI was used to draft or suggest small sections of code and to explain relevant
programming concepts. This included assistance with:

- React components, state, forms, and page navigation
- TypeScript types and frontend API requests
- Flask routes and request handling
- JWT-based authentication and protected endpoints
- Database queries and input validation
- Date, time, calendar, and itinerary-related logic
- CSS layout and interface styling

Suggested code was not copied into the project without review. It was modified
to match the existing file structure, API contracts, database schema, and user
interface.

### 3. Debugging

AI was used to help interpret error messages and identify possible causes of
problems during frontend and backend integration. For example, it assisted in
reasoning about:

- Incorrect API requests or responses
- Authentication and redirect behavior
- React and TypeScript errors
- Data not appearing correctly in itinerary or calendar views
- Styling and layout issues

The team reproduced each issue, evaluated the suggested cause, implemented the
appropriate fix, and tested the affected behavior. AI suggestions that did not
fit the project were discarded.

### 4. Testing and verification

AI helped suggest test cases and edge cases, including invalid form input,
authentication failures, missing data, and unsuccessful API responses. It also
helped explain failures reported by the TypeScript compiler, frontend tests,
linter, or application runtime.

Final verification was performed using the project's own tools and by manually
checking relevant user flows. A suggestion from AI was not considered correct
only because it looked reasonable.

### 5. Documentation

AI was used to help organize and improve written documentation, including this
AI-use record. The team reviewed the generated text and adjusted it to describe
the project and development process accurately.

## Development Workflow

The general workflow for AI-assisted tasks was:

1. A team member described a specific problem or requested an explanation.
2. The AI produced an explanation, example, or possible implementation.
3. The team member reviewed the response and compared it with the project
   requirements and existing code.
4. Useful parts were rewritten or adapted for the application.
5. The resulting change was tested with the relevant project tools and user
   flow.
6. The team member corrected or removed any output that was inaccurate,
   insecure, unnecessary, or inconsistent with the project.

This process kept human review and decision-making at every stage.

## Limitations Encountered

AI responses were not always complete or directly compatible with the project.
Possible problems included:

- Suggestions based on a different library or framework version
- Code that did not match the existing API or database structure
- Valid-looking code with incorrect assumptions
- Incomplete error handling or input validation
- Tests that required adjustment before they represented real behavior
- General solutions that needed to be simplified for this project's scope

Because of these limitations, all output required manual review and project-
specific testing.

## Privacy and Security

AI was not intended to receive passwords, access tokens, API keys, `.env`
contents, private user data, or production database records. Development
questions should use source code and synthetic examples that are safe to share.

Authentication, authorization, input validation, and database changes received
particular attention during review because mistakes in these areas can create
security risks.

## Responsibility for the Final Product

AI acted as an assistant, not as a member of the development team or a
replacement for understanding the code. The human developers are responsible
for:

- The application's requirements and design
- Deciding whether and how AI suggestions were used
- Reviewing and modifying all accepted output
- Testing the final implementation
- Fixing defects and maintaining the project
- Ensuring compliance with course and institutional rules

The final frontend code represents the team's reviewed and integrated work, including
any portions for which AI provided preliminary suggestions.

# AI Use in the Backend Development Process

**Project:** [ItineFairy]
**Started:** [06-18-2026]
**Contributors:** [Ameerah Aguilar, Yafet Yonas]

---

## How to use this file

Add a new entry each time you use an AI prompt that meaningfully contributes to the project. Copy the template block at the bottom and fill it in. Log prompts *as you go*
---

## Entries

---

### [PROMPT-001] [Brainstorm]

| Field        | Detail |
|--------------|--------|
| **Date**     | 06-24-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Get a general Idea of what some ideal languages would be |
| **Phase**    | Research |
| **Outcome**  | Edited |

**Prompt:**
```
I am working on a group project for a tiktok like itinerary app with a 6 week time frame to generate a MVP.
What would be some optimal coding languages to use for an app with features like a feed, built-in calendar, and trip management,
as well as an ideal database to store them. Please include examples for databases, frontend, and backend.
```
**Output summary:**
Gave positives and negatives of various languages, and a loose picture of how they would be used in our project.

**Notes:**
We discussed and agreed that the tiktok feed aspect may be a bit ambitious for our time here, so we opted to void it moving forward.
Ended up settling on a web app with React for frontend, Python Flask framework for backend, and SQLite for our database.

---

### [PROMPT-002] [Skeleton]

| Field        | Detail |
|--------------|--------|
| **Date**     | 06-30-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Create a general outline that we could brainstorm off of |
| **Phase**    | Drafting |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me a code skeleton that compiles all necessary backend files that includes user authentication, a calendar 
export and collaborator compatibility, as well as events that can be managed within a trip. 
```

**Output summary:**
Generated a complete skeleton with comments on each files purpose in the overall project.

**Notes:**
It was a good baseline for a larger scale software project than what we were used to. It overcomplicated the folders a bit, so
we simplified the structure for our own clarity. Also edited the comments for our better understanding.

---

### [PROMPT-003] [Auth Codes]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-02-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Get error codes for authentication |
| **Phase**    | Research |
| **Outcome**  | Edited |

**Prompt:**
```
Can you show me typical error codes and their meanings as they would be used in a user login and sign up authentication file.
```

**Output summary:**
Showed a table of typical codes and their meanings, and showed an example of a return and how it would be used in a json.

**Notes:**
Had to look up some extra codes, but was really helpful in setting up the format for the general return of the whole authentication.

---

### [PROMPT-004] [DB]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-03-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Setup for database |
| **Phase**    | Code |
| **Outcome**  | As-is |

**Prompt:**
```
Can you show me how to setup a database for SQLite in Flask that has a schema with tables containing attributes for reminders, trips, collaborators, itineraries, and authentication. Please ensure that they have surrogate primary keys that give them unique id numbers so that they can easily be referenced. 
```

**Output summary:**
Created a db file that initiated the database, as well as a complete schema with the following tables: trip_collaborator, reminder, itinerary, event, trip, users
sample directly from file:
DROP TABLE IF EXISTS trip_collaborator;
DROP TABLE IF EXISTS reminder;
DROP TABLE IF EXISTS itinerary;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS password_reset_token;
DROP TABLE IF EXISTS trip;
DROP TABLE IF EXISTS users;

**Notes:**
Not a super complex setup, looked through the tables and attributes created, confirmed constraints matched with our project objectives.

---

### [PROMPT-005] [User DB]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-03-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | User data database |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you create queries in user.py to manage and update entries in the database for user data like email, id, and password
```

**Output summary:**
created queries and multiple functions to interact with, retrieve, and update user data within the database

**Notes:**
helpful for database management and useful helpers that were used in routes. Clear and Concise.

---

### [PROMPT-006] [Blueprints]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-06-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Blueprint API Routing |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you show me how to implement blueprint routes 
```

**Output summary:**
Registered routes for auth, collaborators, itineraries, reminders, and trips and initialized them in the __init__.py file
snippet:
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(trips_bp, url_prefix="/api")
app.register_blueprint(itineraries_bp, url_prefix="/api")
app.register_blueprint(reminders_bp, url_prefix="/api")
app.register_blueprint(collaborators_bp, url_prefix="/api")

**Notes:**
Found out there was a way to use blueprints to do api routes and group related routes for our ease of use and readablity.

---

### [PROMPT-007] [Password Reset]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-06-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Password reset Logic |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you create a password reset function in auth.py for users.
```

**Output summary:**
Added forgot password and reset password functions to auth.py. Edited for readability and manually commented.
snippet:
'''
- POST /forgot-password, start a password reset. always says ok even if email is unknown (so no one can guess which emails exist).
- method: POST
- header: Content-Type: application/json
- body(json): email(str, required)
- return {"success":true, "reset_token": <token>, "message":...} (200) if email exists,
-        {"success":true, "message":"If email exists, reset link sent"} (200) if it doesn't,
-        400 if bad/missing json or no email
@auth_bp.route("/forgot-password", methods=['POST'])
- Start a password reset: create a reset token for a known email.
- Always reports success so outsiders can't discover which emails are registered.
def forgot_password():
    data = request.get_json(silent=True)
    
    if not data:
'''
**Notes:**
Worked well in creating the logic, still have to update the fix to make it send live email, would like to expand on the feature in future.

---

### [PROMPT-008] [Password Validation]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-06-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Password validation Logic |
| **Phase**    | Code |
| **Outcome**  | As-is |

**Prompt:**
```
Can you implement a validator helper file to ensure a password is valid only if successfully fits the following criteria:
Minimum 8 character length
Minimum 1 number
Minimum 1 Special character 
Minimum 1 uppercase letter
Minimum 1 lowercase letter
```

**Output summary:**
created validators.py file and a function to check if a password is valid, and only accept it if it falls under those conditions.
Snippet:
def is_valid_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

**Notes:**
Super helpful, it imported re library which was useful in parsing and checking validity, also made us realize we needed and email verification.

---

### [PROMPT-009] [Email Validation]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-06-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Email validation Logic |
| **Phase**    | Code |
| **Outcome**  | As-is |

**Prompt:**
```
Can you also implement a validator function that verifies correct email format when entered by a user.
```

**Output summary:**
Added a function to validators that checks email format.
Snippet:
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))

**Notes:**
Checks validity of email format, doesnt check if email actually exists and is active, would like to expand on the feature in future.

---

### [PROMPT-010] [Trip Model]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-09-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | CRUD functions for trips and events in trip.py |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you write the model functions for trip.py that handle creating, retrieving, updating, and 
deleting a trip, and matching CRUD functions for events tied to a trip_id (including support for 
timezone and an rrule field for recurring events)?
```

**Output summary:**
Generated create_trip, get_trip_by_id, get_trips_by_user, update_trip, delete_trip, plus the matching create_event/get_event_by_id/get_events_by_trip/update_event/delete_event functions.
snippet:
- create trip to the database
- trip_id primary key(int)
- attributes: trip_id(int), name(str), description(str), start_date(date/time), end_date(date/time)
def create_trip(user_id, name, description, start_date, end_date):
    db = get_db()
    
    db.execute(
        "INSERT INTO trip (user_id, name, description, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, description, start_date, end_date)
    )
    
    db.commit()

**Notes:**
Straightforward parallel structure once the schema existed; we reused the same pattern for itinerary.py and reminder.py afterward.

---

### [PROMPT-011] [Login / Signup]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-09-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Login and signup routes using JWT |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you implement /login and /signup routes in auth.py using flask_jwt_extended, checking hashed 
passwords, and returning a JWT on successful login? Make sure signup validates email format, 
password strength, and that passwords match before creating the user.
```

**Output summary:**
Added login() and signup() to auth_bp, wired to is_valid_email/is_valid_password, create_access_token, and identical error messaging for unknown email vs. wrong password.
snippet:


**Notes:**
We specifically asked for the "same error whether email is unknown or password is wrong" behavior after realizing the first draft leaked which emails were registered. Kept separate from prompt 7 since that entry covers forgot/reset password, not login/signup.

---

### [PROMPT-012] [Itinerary Model + Routes]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-14-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Day-by-day itinerary CRUD |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you build the itinerary model and routes so each trip can have a per-day entry (day_number, 
title, description, activities), including get/create/update/delete for a specific trip and day?
```

**Output summary:**
Generated itinerary.py (create_itinerary, get_itinerary_by_id, get_itinerary_by_trip_and_day, get_itinerary_by_trip, update_itinerary, delete_itinerary) and the itineraries_bp GET/POST/PUT/DELETE routes.

**Notes:**
Baseline CRUD pass before completion tracking was added, see prompt 13.

---

### [PROMPT-013] [Itinerary Completion Tracking]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-14-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Mark itinerary days complete/incomplete and track trip progress |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you add the ability to mark a day's itinerary entry as complete or incomplete, and a way to get 
a completion percentage (total vs completed days) for a whole trip?
```

**Output summary:**
Added mark_itinerary_complete/mark_itinerary_incomplete and get_trip_completion_status to itinerary.py, plus the complete, incomplete, and completion-status routes.

**Notes:**
Liked that it returned total/completed/percentage as one object instead of three separate calls.

---

### [PROMPT-014] [Reminders]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-14-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Event reminders with configurable lead time |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you add a reminder model and routes so a user can attach a reminder to an event, specifying 
minutes_before and a notification_type, and be able to list or delete reminders on an event?
```

**Output summary:**
Generated reminder.py (create_reminder, get_reminders_by_event, get_pending_reminders, mark_reminder_sent, delete_reminder) and reminders_bp GET/POST/DELETE routes.

**Notes:**
get_pending_reminders/mark_reminder_sent were included for a future notification worker, hope to build on in the future.

---

### [PROMPT-015] [Collaborators Routes]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-15-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Invite/manage trip collaborators with permission levels |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you write the collaborators routes so a trip owner can invite a collaborator by email, set 
their permission level (viewer/editor), remove them, and let the invited user accept the invitation?
```

**Output summary:**
Generated collaborators_bp with GET/POST/PUT/DELETE on /trips/<trip_id>/collaborators and a separate accept-invitation route, gated so only the trip owner can invite/update/remove.

**Notes:**
Owner-only checks (trip['user_id'] != user_id) were something we specifically asked for after the first pass let any collaborator invite others.

---

### [PROMPT-016] [Recurring Events (RRULE)]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-15-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Expand recurring events into occurrences and validate RRULE strings |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you help me expand recurring events using an RRULE string into individual occurrences within a 
date range, and validate an RRULE before we save it to an event?
```

**Output summary:**
Generated expand_trip_events_raw, expand_recurring_event_raw, and validate_rrule in trip_utils.py using dateutil.rrule, plus the GET /trips/<trip_id>/events?start&end route that expands occurrences in a window.

**Notes:**
This took a couple of follow-up iterations before recurring event dates lined up correctly across timezones.

---

### [PROMPT-017] [Calendar Import/Export (.ics)]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-15-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Export a trip to .ics and import events from an .ics file |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate an .ics file from a trip's events so it can be exported to Google/Outlook/Apple 
calendar, and also parse an incoming .ics file to import events into a trip?
```

**Output summary:**
Generated generate_ics_from_events, parse_ics_file, and import_ics_to_trip in trip_utils.py using the icalendar library, plus the GET /trips/<trip_id>/calendar.ics export route in trips.py.

**Notes:**
Needed a follow-up pass to handle timezone-aware vs naive datetimes correctly when converting to/from UTC.

---

### [PROMPT-018] [App Factory + JWT Setup]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-08-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Wire up Flask app factory, JWT manager, and DB init script |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you show me how to set up a Flask app factory (create_app) that configures JWTManager and 
initializes the SQLite db, plus a one-time init_db.py script to build the tables using schema.sql?
```

**Output summary:**
Generated create_app() in __init__.py, run.py entry point, and init_db.py with a warning comment about DROP TABLE IF EXISTS wiping data on rerun.

**Notes:**
The warning comment in init_db.py about not rerunning against real data was something we asked it to add explicitly after almost wiping test data once. Blueprint registration itself is already covered in PROMPT-006, so this entry only covers the JWT/db-init pieces.

---

### [PROMPT-019] [UserID Bugfix]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-21-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | update return json to include userid in login & signup|
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you update the return value upon successful login to send userid as part of the data so frontend can use it.
```

**Output summary:**
Updated all instances of successful login to include userid as part of it.
Snippet:
return jsonify({
        "success": True,
        "user": {"id": user["id"], "email": user["email"]},
        "token": token
    }), 200

**Notes:**
Shows where AI use can slip up, and how we had to pinpoint the error ourselves through testing and communication to identify and resolve the issue. 

---

### [PROMPT-020] [Requirements]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-26-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | update requirements.txt|
| **Phase**    | Research |
| **Outcome**  | As-is |

**Prompt:**
```
Can you tell me what the command is on mac to pipe to requirements.txt with the updated requirements.
```

**Output summary:**
pip freeze > requirements.txt

**Notes:**
I had to do pip3 freeze > requirements.txt, just needed a quick refresher on freeze command.

---

### [PROMPT-021] [Sign out]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-27-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | sign out|
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
How would the best approach be to implement a sign out feature using jwt token based authentication.
```

**Output summary:**
gave a generic setup for using blocklist to effectively end a token session by adding a jwt id to it.

**Notes:**
Gave the necessary imports, we get to now implement it according to our current standards within our codebase. 

---

### [PROMPT-022] [Auth testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Authentication test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for user authentication that tests signup, login with various credentials, forgot and reset password, and password validity. Create tests to pass edge cases as well and track results.
```

**Output summary:**
generated ~25 user tests that were then tested, and debugged accordingly. 
snippet:
- tests/test_auth.py
import pytest
from flask_jwt_extended import decode_token
from app.models.user import create_password_reset_token, get_user_by_email


- ---------- POST /api/signup ----------

- a valid signup should create the user and return 201
def test_signup_success(client):
    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    assert response.status_code == 201
    assert response.get_json()["success"] is True
    assert response.get_json()["user"]["email"] == "bob@example.com"


**Notes:**
had to add a couple manual cases that we saw fit. Extremely useful for catching a lot of the cases without needed to think of every possible test.

---

### [PROMPT-023] [Itinerary testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Itinerary test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for our itinerary functions including retrieveing and creating itinerary and trip entries, addressing valid day numbers, missing data cases, deleting and completing itineraries, 
```

**Output summary:**
generated ~25 user tests that were then tested, and debugged accordingly. Handled only the direct backend design and logic cases. 
snippet:
- tests/test_itinerary.py
import pytest
from datetime import datetime
from app.models.itinerary import (
    create_itinerary,
    get_itinerary_by_id,
    get_itinerary_by_trip_and_day,
    get_itinerary_by_trip,
    update_itinerary,
    delete_itinerary,
    get_day_date,
    mark_itinerary_complete,
    mark_itinerary_incomplete,
    get_trip_completion_status,
    ValidationError,
)


- ---------- create_itinerary ----------

- creating an itinerary entry should let us find it again by trip + day
def test_create_and_get_itinerary(app):
    with app.app_context():
        create_itinerary(1, 1, "Arrival Day", "Fly in and check into hotel", "Airport, hotel")
        entry = get_itinerary_by_trip_and_day(1, 1)

        assert entry is not None
        assert entry["title"] == "Arrival Day"
        assert entry["description"] == "Fly in and check into hotel"
        assert entry["activities"] == "Airport, hotel"


**Notes:**
had to add a couple manual cases that we saw fit. Also was necessary to do additional testing on the routing to see that the ideal data was returned on the frontend side.

---

### [PROMPT-024] [Itinerary routing testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Itinerary Routing test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for itineraries.py, this time tracking the correct error codes are returned. 
```

**Output summary:**
generated ~20 user tests that were then tested, and debugged accordingly. 
snippet:
- tests/test_reminders_routes.py
import pytest


- helper: creates a trip, returns its id
def make_trip(client, headers):
    response = client.post("/api/trips", json={
        "name": "Test Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
    }, headers=headers)
    return response.get_json()["id"]


**Notes:**
Note to combine the routing and regular testing for future test cases.

---

### [PROMPT-025] [Trip & Trip Routing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Trip logic & Routing test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for trips.py and trip.py, checking both logic cases for all the functions of trip.py like deleting, updating, and managing trips and events. As well as handling collaborators and dealing with duplicates, invites, and etc. Focus on base tests and edge cases. Next make similar test cases, instead on trips.py to handle routing tests that track if the correct data is sent over to frontend. 
```

**Output summary:**
generated ~60 user tests that were then tested, and debugged accordingly. About half for routing and half for regular.
snippet:
- ---------- create_trip / get_trip_by_id ----------

- creating a trip should let us find it again by id + owning user
def test_create_and_get_trip(app):
    with app.app_context():
        create_trip(1, "Paris Vacation", "A week in Paris",
                     datetime(2026, 6, 1), datetime(2026, 6, 8))

        trips = get_trips_by_user(1)
        trip = trips[-1]

        assert trip["name"] == "Paris Vacation"
        assert trip["description"] == "A week in Paris"

        fetched = get_trip_by_id(trip["id"], 1)
        assert fetched is not None
        assert fetched["name"] == "Paris Vacation"

Routes Snippet:
import pytest
import json


- ---------- auth / access control ----------

- no Authorization header should return 401
def test_get_trips_no_auth_header(client):
    response = client.get("/api/trips")
    assert response.status_code == 401

- a garbage/invalid token should return 401, not crash with a 500
def test_get_trips_invalid_auth_header(client):
    response = client.get("/api/trips", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 422

**Notes:**
Learning to expand prompts so we can get everthing we need at the same time. Need to add tests for date time and formatting for a lot of the trip functions.
---

### [PROMPT-026] [Trip Utility testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Trip formatting calendar & datetime |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me test cases to ensure that date time formatting as well as calencar (ics) is all valid, as well as rrule for recurring events. 
```

**Output summary:**
Generated tests for misc. 
Snippet:
- tests/test_trip_utils.py
import pytest
from datetime import datetime
from app.utils.trip_utils import (
    validate_rrule,
    expand_recurring_event_raw,
    expand_trip_events_raw,
    generate_ics_from_events,
)


- ---------- validate_rrule ----------

- a well-formed weekly rrule should validate successfully
def test_validate_rrule_valid_weekly():
    valid, error = validate_rrule("FREQ=WEEKLY;BYDAY=MO")
    assert valid is True
    assert error is None



**Notes:**
Useful in solidifying and ensuring cohesiveness of our program. 
---

### [PROMPT-027] [Reminder & Reminder Routing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Reminder logic & Routing test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for reminder.py and reminders.py similar to the trips tests that checks both routing and token generation as well as base logic. This should include creation and retrieving reminders, notifications, correct time and dates, and tracking and deleting reminders. 
```

**Output summary:**
generated ~40 user tests that were then tested, and debugged accordingly. About half for routing and half for regular.
snippet:
- tests/reminder_test.py
import pytest
from datetime import datetime, timedelta
from app.models.trip import create_trip, get_trips_by_user, create_event, get_events_by_trip
from app.models.reminder import (
    create_reminder,
    get_reminders_by_event,
    get_reminder_by_id,
    get_pending_reminders,
    mark_reminder_sent,
    delete_reminder,
    ValidationError,
)


- helper: creates a trip + one event on it, returns the event dict
def make_event(app, start_time=datetime(2026, 6, 2, 10, 0), end_time=datetime(2026, 6, 2, 12, 0)):
    create_trip(1, "Test Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 10))
    trip = get_trips_by_user(1)[-1]
    create_event(trip["id"], "Test Event", "desc", start_time, end_time, "UTC", None)
    return get_events_by_trip(trip["id"])[-1]

Routes Snippet:
- tests/test_reminders_routes.py
import pytest


- helper: creates a trip, returns its id
def make_trip(client, headers):
    response = client.post("/api/trips", json={
        "name": "Test Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
    }, headers=headers)
    return response.get_json()["id"]
---

### [PROMPT-028] [Collaborators & Collab Routing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Collaborators logic & Routing test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me backend test cases for collaborators and check that it routes correctly as well. I want to test that collaborators are working with their given permission levels, and that missing data results in errors like updating the wrong trip or inviting an invalid user. I also want to check routing for functions like removing, accepting invites, and updating collaborators.
```

**Output summary:**
generated ~20 user tests that were then tested, and debugged accordingly. About half for routing and half for regular.
snippet:
- tests/collaborators_routes_test.py
import pytest


- helper: creates a trip owned by given user (via their auth headers), returns its id
def make_trip(client, headers):
    response = client.post("/api/trips", json={
        "name": "Test Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
    }, headers=headers)
    return response.get_json()["id"]

---

### [PROMPT-029] [Validators testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Validators test cases |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you generate me a validators test that tests formats for emails and passwords and check that they are correct and bypass the requirements.
```

**Output summary:**
Generated some simple user tests as a baseline that were added onto as we thought of more test cases.
snippet:
- tests/test_validators.py
import pytest
from app.utils.validators import is_valid_email, is_valid_password


- ---------- is_valid_email ----------

- a properly formatted email should return True
def test_is_valid_email_valid():
    assert is_valid_email("bob@example.com") is True

- missing @ symbol should be rejected
def test_is_valid_email_missing_at_symbol():
    assert is_valid_email("bobexample.com") is False


**Notes:**
had to add a couple manual cases that we saw fit. Final test case that was implemented.

---

### [PROMPT-030] [Conftest testing]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-25-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | conftest test setup |
| **Phase**    | Code |
| **Outcome**  | As-is |

**Prompt:**
```
Can you generate me a file with a temporary database that I can use to test which creates a new flask app instance for my test cases. 
```

**Output summary:**
snippet:
import os
import tempfile
import pytest
from app import create_app
from app.db import get_db


"""
Sets up a temporary database for testing
Provides fixtures for the Flask app and test client.

Creates a temporary SQLite database
Initializes the schema
Yields the app and client for use in tests.
"""

- path to schema.sql relative to THIS file, so it works no matter where the tests are run from
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema.sql")


- Creates a fresh Flask app with a temporary, empty test database
- runs before every test that uses it
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })
    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH) as f:
            db.executescript(f.read())
        db.commit()
        yield app
    os.close(db_fd)
    os.unlink(db_path)


- Fake HTTP client for the Flask app, used to make requests in tests
@pytest.fixture
def client(app):
    return app.test_client()


**Notes:**
Necessary for testing, created before all test cases were executed.

---

### [PROMPT-031] [ReadMe Generation]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-08-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | create readME |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can you create a readME file that shows a brief introduction of our repository, and how to navigate it. 
```

**Output summary:**
Generated a readMe file that we added and deleted as we saw fit to keep simplicity, while retaining the core of our project.

---

### [PROMPT-032] [Signout Test]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-27-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Testing for signout fix |
| **Phase**    | Code |
| **Outcome**  | Edited |

**Prompt:**
```
Can give me a test with curl commands to check if my signout functions routing works and that it correctly revokes token access upon completion.
```

**Output summary:**
Gave me a list of curl commands and testing procedure to follow to test before pushing to frontend. 
snippet:
Here's the full sequence, in order, after restarting your server:

1. Sign up (only needed if this user doesn't already exist — skip if you already created it):

curl -X POST http://localhost:5001/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"TestPass1!","confirm_password":"TestPass1!"}

**Notes:**
Reminded me about how useful AI is in doing tests like these. Quickly generated a test user, had to ask it to remake a password with proper requirements.

---

### [PROMPT-033] [AI prompt outline]

| Field        | Detail |
|--------------|--------|
| **Date**     | 07-13-2026 |
| **Model**    | Claude Sonnet 5.0 |
| **Purpose**  | Generate Template for AI prompts |
| **Phase**    | Drafting |
| **Outcome**  | Edited |

**Prompt:**
```
I have to record all AI prompts that were used throughout the project, I would like a template where I can input each of the prompts with their outputs and how they assisted our group throughout the project.
```

**Output summary:**
Generated a template with an entry and summary table that could be added upon.
 <!-- ============================================================ TEMPLATE — copy this block for each new entry ============================================================ ### [PROMPT-XXX] [Short descriptive title] | Field | Detail | |--------------|--------| | **Date** | | | **Model** | | | **Purpose** | | | **Phase** | | | **Outcome** | Used as-is / Edited / Discarded | **Prompt:** ``` (paste prompt here) ``` **Output summary:** **Notes:** --- ============================================================ -->
Summary table
Keep this updated as a quick reference across all entries.

---
## Summary table

Keep this updated as a quick reference across all entries.

| ID | Title | Date | Model | Phase | Outcome |
|----|-------|------|-------|-------|---------|
| PROMPT-001 | Brainstorm | 06-24-2026 | Claude Sonnet 5.0 | Research | Edited |
| PROMPT-002 | Skeleton | 06-30-2026 | Claude Sonnet 5.0 | Drafting | Edited |
| PROMPT-003 | Auth Codes | 07-02-2026 | Claude Sonnet 5.0 | Research | Edited |
| PROMPT-004 | DB | 07-03-2026 | Claude Sonnet 5.0 | Code | As-is |
| PROMPT-005 | User DB | 07-03-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-006 | Blueprints | 07-06-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-007 | Password Reset | 07-06-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-008 | Password Validation | 07-06-2026 | Claude Sonnet 5.0 | Code | As-is |
| PROMPT-009 | Email Validation | 07-06-2026 | Claude Sonnet 5.0 | Code | As-is |
| PROMPT-010 | Trip Model | 07-09-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-011 | Login / Signup | 07-09-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-012 | Itinerary Model + Routes | 07-14-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-013 | Itinerary Completion Tracking | 07-14-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-014 | Reminders | 07-14-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-015 | Collaborators Routes | 07-15-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-016 | Recurring Events (RRULE) | 07-15-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-017 | Calendar Import/Export (.ics) | 07-15-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-018 | App Factory + JWT Setup | 07-08-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-019 | UserId fix | 07-21-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-020 | Requirements | 07-26-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-021 | Sign Out | 07-27-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-022 | Auth Testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-023 | Itinerary Testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-024 | Itinerary Route test | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-025 | Trip Testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-026 | Trip Utility testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-027 | Reminder Testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-028 | Collaborators testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-029 | Validators testing | 07-25-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-030 | Conftest testing | 07-25-2026| Claude Sonnet 5.0 | Code | Edited |
| PROMPT-031 | ReadMe | 07-08-2026 | Claude Sonnet 5.0 | Code | Edited |
| PROMPT-032 | Signout Test | 07-26-2026 | Claude Sonnet 5.0 | Code | Edited |
