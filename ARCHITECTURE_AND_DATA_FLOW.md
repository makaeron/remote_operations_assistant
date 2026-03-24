# Architecture and Data Flow

## Project purpose

The Remote Operations Assistant helps remote operators monitor many industrial sites from one place.

It answers:
- Which site needs attention first?
- What happened?
- What should the remote operator do next?
- Which local runbook supports that action?

---

## Main architecture layers

### 1. Input layer
This is where the first input enters the project.

Possible sources:
- simulated site alarms
- real SCADA events
- REST event producer
- future MQTT consumer

In this starter version, input enters through:

`POST /events`

---

### 2. Validation layer
FastAPI + Pydantic validate the event.

Checks include:
- required fields are present
- field types are valid
- payload shape is correct

---

### 3. Persistence layer
The event is stored in SQLite.

Tables:
- `events`
- `incidents`

---

### 4. Scoring layer
The rules engine gives the event a score.

Example:
- high severity alarm = high score
- critical motor fault = even higher score
- repeated failed login burst = urgent cyber-operational issue

---

### 5. Incident generation layer
If the event score crosses a threshold, the system creates an active incident.

This gives operators a cleaner view than watching every raw event one by one.

---

### 6. Retrieval layer
The project then retrieves the most relevant local runbooks.

Current retrieval context:
- site ID
- asset type
- event type

This makes retrieval more site-aware and asset-aware.

---

### 7. Action generation layer
The retrieved runbooks are converted into a ranked action list.

Example output:
- confirm telemetry freshness
- compare recent trend
- verify network link
- notify maintenance or cyber operations

---

### 8. Cross-site prioritization layer
All active incidents are sorted by urgency.

This allows one remote operator to decide where to start first.

---

### 9. Operator output layer
The operator views the results by calling:

- `GET /ops/incidents`
- `GET /ops/ranked-actions`
- `GET /ops/shift-summary`

---

## Step-by-step data flow

### A. User/system input starts here
A remote site, simulator, or upstream system sends an event to:

`POST /events`

### B. Event is validated
FastAPI checks the JSON structure.

### C. Event is stored
The event goes into the `events` table.

### D. Rules engine scores the event
The backend gives it an operational priority score.

### E. Incident is created when needed
If the score is high enough, an entry is created in the `incidents` table.

### F. Knowledge lookup happens
The RAG service searches local runbooks using:
- site
- asset
- event type

### G. Recommended actions are generated
The backend extracts practical steps from the runbooks.

### H. Incidents are ranked
The prioritization service sorts incidents by urgency.

### I. Remote operator sees final output
The API returns:
- active incidents
- ranked action list
- shift summary

---

## Simple flow diagram

```text
Site Event / Simulator
        |
        v
POST /events
        |
        v
FastAPI Validation
        |
        v
Store Raw Event in SQLite
        |
        v
Rules Engine Score
        |
        +---- low score ----> keep only as event
        |
        +---- high score ---> create incident
                                |
                                v
                          Retrieve runbooks
                                |
                                v
                        Build recommended actions
                                |
                                v
                      Rank incidents across sites
                                |
                                v
                 /ops/incidents | /ops/ranked-actions | /ops/shift-summary
```

---

## Where the LLM would fit later

In this starter version, action generation is rule-based and retrieval-based.

If you later add an LLM, it should sit after retrieval:

`Retrieved docs -> LLM -> cleaner explanation + operator summary`

That is better than using the LLM as the raw input source.
