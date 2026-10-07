## Run locally

This is a FastAPI application. Use Python 3.10 or newer and run the commands below from the repository root on macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is served at <http://127.0.0.1:8000>, interactive API documentation is at <http://127.0.0.1:8000/docs>, and the health response is at <http://127.0.0.1:8000/>.

### Services and credentials

Startup requires a reachable MySQL server with credentials that can create/use `real_estate_db`. The property routes also initialize Backblaze B2 during application import, so valid B2 credentials and network access are required even if you are not uploading files. These connection settings are currently hardcoded in the application; move them to environment variables and rotate any credentials that have been committed or shared before deploying.

For development, keep the Uvicorn process running in the terminal. Stop it with Ctrl+C.
