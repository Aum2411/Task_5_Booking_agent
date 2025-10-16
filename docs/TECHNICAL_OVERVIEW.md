# BookMyTurf — Technical Overview

This document explains the approach, design decisions, how the agent works, constraints and assumptions, challenges and fixes, and how to set up and run the project on a local machine. It’s written for developers and power users.

---

## 1) Problem & Approach

Goal: Build an AI-powered booking agent for a sports turf that can:
- Understand natural language requests (chat-first UX)
- Check availability and pricing
- Create and cancel bookings
- Present a clean, modern UI with responsive web design (HTML + advanced CSS)

Approach:
- Frontend: Single-page style experience rendered by Flask using Jinja templates. Modern CSS for animations, gradients, and glassmorphism.
- Backend: Flask REST endpoints and chat route. Business logic encapsulated in two Python components:
  - `TurfBookingDatabase` (JSON storage) for turfs and bookings
  - `TurfBookingAgent` (Groq LLM) for conversational flow
- Storage: Lightweight JSON file (`bookings.json`) to avoid DB setup friction. Easy to migrate to SQLite/Postgres later.
- AI: Groq Chat Completions API with LLaMA 3.3 for fast, cost‑efficient reasoning and natural language.

Key design choice: Separate the AI layer (dialog + intent) from the booking layer (availability, pricing, persistence). This keeps the system maintainable and testable.

---

## 2) High‑Level Architecture

```
+------------------------+       +--------------------+
|      Web Browser       | <---> |      Flask App     |
|  HTML/CSS/JS (UI/UX)   |       |  app.py            |
+-----------+------------+       +----------+---------+
            |                               |
            |  /chat (LLM)                  |  /api/* (CRUD)
            v                               v
     +------+----------------+      +-------+----------------+
     |  TurfBookingAgent     |      |  TurfBookingDatabase  |
     |  (agent.py, Groq LLM) |      |  (database.py, JSON)  |
     +-----------+-----------+      +-----------+------------+
                 |                               |
                 |  model: llama-3.3-70b-...     |  file: bookings.json
                 v                               v
          +---------------+                 +-------------+
          |  Groq API     |                 |  JSON Store |
          +---------------+                 +-------------+
```

Data flow:
1. User sends a chat message from UI → `/chat` → Agent builds prompt and calls Groq → response back to UI.
2. For bookings/availability, the backend hits `/api/*` endpoints that call `TurfBookingDatabase` to read/write `bookings.json`.

---

## 3) Core Components

### 3.1 Database layer (`database.py`)
Responsibilities:
- Initialize a dummy turf
- List turfs
- Check availability
- Create/cancel bookings
- Persist everything to `bookings.json`

Key methods (snippets abbreviated for clarity):

```python
class TurfBookingDatabase:
    def initialize_dummy_turf(self):
        if not self.data["turfs"]:
            self.data["turfs"] = [{
                "id": "turf_001",
                "name": "Green Valley Sports Arena",
                "price_per_hour": 1500,
                "available_hours": ["06:00", ..., "22:00"],
                # ... amenities, rating, etc.
            }]
            self.save_data()

    def check_availability(self, turf_id: str, date: str, time_slot: str) -> bool:
        bookings = self.get_bookings_for_date(turf_id, date)
        return all(not (b["time_slot"] == time_slot and b["status"] == "confirmed")
                   for b in bookings)

    def create_booking(self, booking_data: Dict) -> Dict:
        booking_id = f"BK{len(self.data['bookings']) + 1:04d}"
        booking = { **booking_data, "booking_id": booking_id, "status": "confirmed" }
        self.data["bookings"].append(booking)
        self.save_data()
        return booking
```

Design decisions:
- JSON store to keep things simple and portable; no server dependency.
- Booking IDs are sequential and human‑readable for easy reference.

Edge cases handled:
- Slot conflicts (prevent double‑booking)
- Missing turf IDs
- No turfs/bookings yet

---

### 3.2 Agent layer (`agent.py`)
Responsibilities:
- Maintain chat history (short window for context)
- Build a domain‑specific system prompt with current turf data
- Delegate CRUD logic to the database layer

Important fields:

```python
self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
self.model = "llama-3.3-70b-versatile"  # updated from decommissioned 3.1 model
```

Message processing:

```python
def process_message(self, user_message: str) -> str:
    self.conversation_history.append({"role": "user", "content": user_message})

    # lightweight command hooks before LLM call
    quick = self._handle_special_commands(user_message)
    if quick:
        self.conversation_history.append({"role": "assistant", "content": quick})
        return quick

    messages = [{"role": "system", "content": self.get_system_prompt()}] \
               + self.conversation_history[-10:]

    chat_completion = self.client.chat.completions.create(
        messages=messages,
        model=self.model,
        temperature=0.7,
        max_tokens=1024,
    )
    ai_response = chat_completion.choices[0].message.content
    self.conversation_history.append({"role": "assistant", "content": ai_response})
    return ai_response
```

Special commands bypass the LLM for speed/consistency:
- “check availability” → direct DB lookup
- “show bookings” → list recent bookings

System prompt strategies:
- Clear, domain‑specific instructions
- Explicit date/time formats
- Guidance for stepwise booking flow (ask name → phone → date → time → confirm)

---

### 3.3 Web layer (`app.py`)
REST + chat endpoints:

```python
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = agent.process_message(data.get('message', ''))
    return jsonify({ 'response': response, 'timestamp': datetime.now().strftime('%H:%M') })

@app.route('/api/book', methods=['POST'])
def create_booking():
    data = request.json
    # validate, check availability, compute amount, persist
    booking = agent.create_booking_from_details(data)
    return jsonify({ 'success': True, 'booking': booking })
```

Frontend (`templates/index.html` + `static/*`):
- Responsive layout with sections for hero, turfs, bookings, chat
- JS enhances UX (smooth scroll, quick‑actions, chat rendering)
- Advanced CSS (gradients, glassmorphism, animations, custom scrollbar)

---

## 4) Design Decisions

- Simplicity first: JSON store and a single turf keep the demo focused
- Clear separation of concerns: agent vs. data_access vs. web
- Groq LLaMA 3.3 model for longevity and performance (3.1 was decommissioned)
- Defensive programming in API routes (field validation, 4xx on bad input)
- Stateless UI: server renders the shell; JS fetches data as needed

Alternatives considered:
- SQL database for ACID guarantees (tradeoff: setup friction)
- Server‑side rendering for chat (tradeoff: interactivity)
- Multi‑turf support (kept as straightforward future extension)

---

## 5) Challenges & Fixes

- Groq client proxies error: Resolved by upgrading `groq` package.
- Decommissioned model `llama-3.1-70b-versatile`: Switched to `llama-3.3-70b-versatile`.
- Idempotent bookings: Prevented duplicate slot bookings by checking conflicts before commit.
- UI/UX polish: Ensured mobile responsiveness, added quick actions and animations.

---

## 6) Assumptions & Constraints

- Single timezone and currency (IST / ₹) for simplicity
- One dummy turf pre‑loaded; easy to add more
- Hourly slots only (e.g., 06:00, 07:00, …, 22:00)
- No payments/auth yet; focus is on booking flow
- JSON file is the source of truth; no concurrent writers

---

## 7) Setup on a Local Machine (Windows PowerShell)

Prerequisites:
- Python 3.10+ installed
- Groq API key in a `.env` file at the project root (`GROQ_API_KEY=...`)

Install and run:

```powershell
# from the project root
pip install -r requirements.txt
python app.py
```

Open the app:
- http://127.0.0.1:5000

Troubleshooting:
- If you see a model decommission error, confirm `agent.py` uses `llama-3.3-70b-versatile`.
- If `groq` import errors occur, upgrade the package:

```powershell
pip install --upgrade groq
```

- If port 5000 is in use, run Flask on another port:

```powershell
$env:FLASK_RUN_PORT=5001; python app.py
```

---

## 8) How the Agent Works (Step‑by‑Step)

1. User enters a message in the chat box
2. Frontend POSTs to `/chat` with `{ message }`
3. Agent composes `[system] + last 10 messages` and calls Groq
4. LLM produces a conversational reply (may ask for missing details)
5. For explicit commands or when enough info is present, the server:
   - Checks availability against `bookings.json`
   - Calculates cost based on duration × price_per_hour
   - Stores booking with an ID (e.g., BK0001)
6. Response returns to the UI, which renders it with subtle animations
7. The bookings section fetches `/api/bookings` to show current reservations

---

## 9) Extensibility

- Multi‑turf inventory: add more entries to `turfs` and expose a selector in UI
- Calendar view: client‑side calendar component calling `/api/availability`
- Payments: integrate a gateway, capture transaction IDs in bookings
- Notifications: email/SMS confirmations via providers like SendGrid/Twilio
- Auth: per‑user accounts and booking history
- DB migration: move from JSON to SQLite/Postgres with an ORM

---

## 10) Testing Ideas

- Unit tests for `TurfBookingDatabase` (availability, create/cancel)
- Contract tests for `/api/*` endpoints
- Mock LLM for deterministic chat tests
- UI smoke tests (Cypress/Playwright) for booking flow

---

## 11) Files of Interest

- `app.py` — Flask app and REST endpoints
- `agent.py` — Groq client + chat orchestration
- `database.py` — JSON persistence and turf/booking logic
- `templates/index.html` — Main UI
- `static/css/style.css` — Advanced styling
- `static/js/script.js` — Frontend behaviors & chat

---

Built for clarity, speed, and easy iteration. Enjoy exploring and extending BookMyTurf!
