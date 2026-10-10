## Run locally

This is a FastAPI application. Use Python 3.10 or newer and run the commands below from the `backend` folder on macOS:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is served at <http://127.0.0.1:8000>, interactive API documentation is at <http://127.0.0.1:8000/docs>, and the health response is at <http://127.0.0.1:8000/>.

### Services and credentials

Startup requires a reachable MySQL server with credentials that can create/use `real_estate_db`. Backblaze B2 settings are loaded from the backend `.env` file. Copy `backend/.env.example` to `backend/.env` and fill in the local values before starting the app. Keep `.env` private; it is ignored by Git.

For development, keep the Uvicorn process running in the terminal. Stop it with Ctrl+C.


### Google sign-in

Set `GOOGLE_CLIENT_ID` in the backend environment and `VITE_GOOGLE_CLIENT_ID` in the frontend environment to the same Web OAuth client ID from Google Cloud Console. Add the local frontend origin (for example, `http://localhost:3000`) to the OAuth client's authorized JavaScript origins. Google ID tokens are verified by the backend before an account is created or signed in.

### Buyer, property, and agent workflow

Properties have an optional `agent_id`, separate from `owner_id`. On startup, the app adds this nullable column and index to an existing database; older properties remain unassigned until an owner or admin assigns an agent.

Use the authenticated API in this order:

1. An owner or admin lists available agents with `GET /users/agents`, then assigns one using `PUT /properties/{property_id}/agent` with `{"agent_id": 12}`.
2. The assigned agent sees their properties with `GET /properties/assigned-to-me`.
3. A buyer's viewing request is created with `POST /bookings/{property_id}`. The agent sees requests for their assigned properties at `GET /bookings/agent` and can confirm, cancel, or complete a request with `PUT /bookings/{booking_id}`.
4. A buyer starts a property conversation with `POST /chat/send`, setting `property_id` and `receiver_id` to the property's `agent_id`. The agent's inbox is `GET /chat/agent/inbox`.
5. The agent replies through the same `POST /chat/send` endpoint, using the same `property_id` and the buyer's ID as `receiver_id`. Read that thread with `GET /chat/property/{property_id}/conversation/{buyer_id}`.

Send the login access token as a bearer token. The backend checks that the authenticated owner can assign the property, the selected account is an active agent, and property messages go only between the buyer and that property's assigned agent.
