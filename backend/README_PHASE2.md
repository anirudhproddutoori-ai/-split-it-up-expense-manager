# splitUP Backend - Phase 2: Core Logic (In-Memory)

This is Phase 2 of the splitUP backend implementation. It provides complete backend logic using in-memory storage (no database) and mock authentication.

## Features Implemented

✅ **Group Management**
- Create groups
- Join groups via invite code
- List user's groups
- Get group details

✅ **Expense Management**
- Add expenses to groups
- List expenses for a group
- Equal split calculation

✅ **Balance Calculation**
- Calculate balances based on expenses
- Show who owes whom
- Detailed balance breakdown

## Project Structure

```
backend/
├── main.py                 # FastAPI app entrypoint
├── models/                 # Pydantic schemas
│   ├── __init__.py
│   ├── group.py           # Group models
│   ├── expense.py         # Expense models
│   └── balance.py         # Balance models
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── groups.py          # Group endpoints
│   ├── expenses.py        # Expense endpoints
│   └── balances.py        # Balance endpoints
├── data/                   # In-memory storage
│   ├── __init__.py
│   └── storage.py         # Storage dictionaries and helpers
└── requirements_phase2.txt # Minimal dependencies
```

## Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements_phase2.txt
```

## Running the Server

```bash
# From the backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000/api
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Mock Authentication

For Phase 2, a mock user is hardcoded:
- **User ID**: `user_123`
- **User Name**: `Test User`

All endpoints assume this user is logged in. This will be replaced with real authentication in later phases.

## API Endpoints

### Groups

- `POST /api/groups` - Create a new group
- `POST /api/groups/join` - Join a group with invite code
- `GET /api/groups` - List all groups for current user
- `GET /api/groups/{group_id}` - Get group details

### Expenses

- `POST /api/groups/{group_id}/expenses` - Add an expense
- `GET /api/groups/{group_id}/expenses` - List expenses

### Balances

- `GET /api/groups/{group_id}/balances` - Get balance summary

## Example Usage

### 1. Create a Group

```bash
curl -X POST "http://localhost:8000/api/groups" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Apartment 402",
    "type": "home",
    "currency": "INR"
  }'
```

Response includes an `invite_code` that others can use to join.

### 2. Join a Group

```bash
curl -X POST "http://localhost:8000/api/groups/join" \
  -H "Content-Type: application/json" \
  -d '{
    "invite_code": "X8J2-9K"
  }'
```

### 3. Add an Expense

```bash
curl -X POST "http://localhost:8000/api/groups/{group_id}/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dinner at SpiceHub",
    "amount": 1200.0,
    "paid_by": "user_123",
    "category": "Food",
    "split_type": "equal"
  }'
```

### 4. Get Balances

```bash
curl "http://localhost:8000/api/groups/{group_id}/balances"
```

## Data Storage

All data is stored in memory using Python dictionaries:
- `groups_storage`: Stores groups
- `expenses_storage`: Stores expenses
- `users_storage`: Simple user lookup (minimal for Phase 2)

**Important**: All data is lost when the server restarts. This is intentional for Phase 2.

## Error Handling

The API returns appropriate HTTP status codes:
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input or business logic error
- `403 Forbidden` - User not authorized (not a group member)
- `404 Not Found` - Resource not found

All errors include a `detail` field with a human-readable message.

## Limitations (By Design)

Phase 2 intentionally does NOT include:
- ❌ Database persistence (uses in-memory storage)
- ❌ Real authentication (uses mock user)
- ❌ User management (hardcoded users)
- ❌ Payment/settlement tracking
- ❌ Debt simplification
- ❌ Activity feed
- ❌ Notifications

These will be added in later phases.

## Next Steps

After Phase 2, you can:
1. Integrate this backend with the frontend
2. Add database persistence (Phase 3)
3. Add real authentication (Phase 4)
4. Add advanced features (payments, debt simplification, etc.)

## Testing

You can test the API using:
- Interactive docs at `/docs` (Swagger UI)
- Alternative docs at `/redoc`
- curl commands (see examples above)
- Postman or similar tools
