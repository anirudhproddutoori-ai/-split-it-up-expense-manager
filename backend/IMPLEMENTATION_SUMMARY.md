# Phase 2 Implementation Summary

## Overview

Phase 2 implements the core backend logic for splitUP using FastAPI with in-memory storage. All data is stored in Python dictionaries and is lost when the server restarts. This is intentional for this phase.

## File Structure & Purpose

### `main.py` - Application Entrypoint
- Creates the FastAPI app
- Configures CORS middleware (allows frontend connections)
- Includes all route modules
- Defines root and health check endpoints
- **Key**: Mock user constants (`CURRENT_USER_ID`, `CURRENT_USER_NAME`) are defined here

### `models/` - Data Schemas (Pydantic)

#### `models/group.py`
- **GroupCreate**: Request schema for creating a group (name, type, currency, simplify_debts)
- **GroupJoin**: Request schema for joining a group (invite_code)
- **GroupResponse**: Response schema with full group details including members
- **GroupMember**: Member information (user_id, name, role, joined_at)

#### `models/expense.py`
- **ExpenseCreate**: Request schema for creating an expense (title, amount, paid_by, category, split_type, date)
- **ExpenseResponse**: Response schema with full expense details including splits
- **ExpenseSplit**: How an expense is split (user_id, amount_owed)

#### `models/balance.py`
- **BalanceResponse**: Complete balance summary for a user
  - `your_balance`: Net balance (positive = owed to you, negative = you owe)
  - `you_owe`: Total amount you owe
  - `you_are_owed`: Total amount owed to you
  - `people_you_owe`: List of people you owe money to
  - `people_who_owe_you`: List of people who owe you money
- **PersonBalance**: Balance with a specific person (user_id, name, amount)

### `routes/` - API Endpoints

#### `routes/groups.py`
Handles all group operations:
- **POST `/api/groups`**: Create a new group
  - Generates unique group ID and invite code
  - Sets current user as admin and first member
- **POST `/api/groups/join`**: Join a group with invite code
  - Validates invite code exists
  - Prevents duplicate membership
- **GET `/api/groups`**: List all groups where current user is a member
- **GET `/api/groups/{group_id}`**: Get group details
  - Validates user is a member (403 if not)

#### `routes/expenses.py`
Handles expense operations for a group:
- **POST `/api/groups/{group_id}/expenses`**: Create an expense
  - Validates group exists and user is a member
  - Validates paid_by user is a group member
  - Splits expense equally among all members
  - Creates ExpenseSplit records for each member
- **GET `/api/groups/{group_id}/expenses`**: List all expenses
  - Returns expenses sorted by date (most recent first)
  - Only accessible to group members

#### `routes/balances.py`
Calculates balances from expenses:
- **GET `/api/groups/{group_id}/balances`**: Get balance summary
  - Calculates how much current user owes/is owed
  - Breaks down by individual people
  - Logic:
    1. If current user paid: others owe their share
    2. If someone else paid: current user owes their share
    3. Net balance = (owed to you) - (you owe)

### `data/storage.py` - In-Memory Storage

Three main storage dictionaries:
- **`groups_storage`**: `{group_id: group_dict}` - All groups
- **`expenses_storage`**: `{expense_id: expense_dict}` - All expenses
- **`users_storage`**: `{user_id: user_dict}` - Simple user lookup

Helper functions:
- **`generate_group_id()`**: Creates unique group ID (`group_1234`)
- **`generate_expense_id()`**: Creates unique expense ID (`expense_12345`)
- **`generate_invite_code()`**: Creates unique invite code (`X8J2-9K` format)
- **`get_user_name(user_id)`**: Returns user name or user_id if not found
- **`add_user(user_id, name, email)`**: Adds user to storage (called when joining groups)

## Key Design Decisions

### 1. Equal Split Only (Phase 2)
- Only "equal" split type is supported
- Expenses are divided equally among all group members
- Future: Support custom splits, percentages, exact amounts

### 2. Mock Authentication
- Hardcoded `CURRENT_USER_ID = "user_123"` and `CURRENT_USER_NAME = "Test User"`
- All endpoints assume this user is logged in
- Future: Replace with JWT/session-based auth

### 3. In-Memory Storage
- No database persistence
- All data lost on restart
- Simple dictionary-based storage
- Future: Replace with MongoDB/PostgreSQL

### 4. Simple Balance Calculation
- Calculates from expenses only
- No debt simplification (even though field exists in Group model)
- No payment/settlement tracking
- Future: Add settlement records, debt simplification algorithm

### 5. Error Handling
- Consistent HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request (invalid input, business logic error)
  - 403: Forbidden (not a member)
  - 404: Not Found (group/expense doesn't exist)
- All errors include `detail` field with human-readable message

## Testing the API

### Start the server:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive Docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example Requests:

**1. Create a group:**
```bash
curl -X POST "http://localhost:8000/api/groups" \
  -H "Content-Type: application/json" \
  -d '{"name": "Apartment 402", "type": "home"}'
```

**2. Join a group:**
```bash
curl -X POST "http://localhost:8000/api/groups/join" \
  -H "Content-Type: application/json" \
  -d '{"invite_code": "X8J2-9K"}'
```

**3. Add an expense:**
```bash
curl -X POST "http://localhost:8000/api/groups/group_1234/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dinner at SpiceHub",
    "amount": 1200.0,
    "paid_by": "user_123",
    "category": "Food"
  }'
```

**4. Get balances:**
```bash
curl "http://localhost:8000/api/groups/group_1234/balances"
```

## Next Steps (Future Phases)

### Phase 3: Database Integration
- Replace in-memory storage with MongoDB/PostgreSQL
- Add persistence layer
- Add database models/ORM

### Phase 4: Authentication
- Replace mock user with JWT tokens
- Add Google OAuth
- Add user registration/login endpoints
- Add authentication middleware

### Phase 5: Advanced Features
- Custom expense splits (percentages, exact amounts)
- Payment/settlement tracking
- Debt simplification algorithm
- Activity feed
- Notifications
- Group settings (edit, delete, leave)
- Expense editing/deletion

## Code Quality Notes

- ✅ All functions have docstrings
- ✅ Type hints used throughout
- ✅ Pydantic validation on all inputs
- ✅ Consistent error handling
- ✅ Helper functions for validation
- ✅ Clear variable names
- ✅ Comments explain complex logic (especially balance calculation)

The code is designed to be:
- **Readable**: Easy to understand by a college student
- **Extensible**: Easy to add database/auth later
- **Correct**: Handles edge cases (invalid IDs, unauthorized access, etc.)
