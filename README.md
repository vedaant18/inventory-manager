# Inventory Manager (Flask + SQLite)

A minimal inventory management web app using Flask and SQLite. View your inventory, add new items, increase/decrease quantities, and delete items.

## Features

- List all inventory items
- Add a new item (or increase an existing item's quantity)
- Adjust quantity up or down (cannot go below 0)
- Delete an item
- SQLite database stored locally as `inventory.db`

## Requirements

- Python 3.10+ recommended
- Windows PowerShell (steps below are Windows-focused, but it also works on macOS/Linux)
- Optional: PostgreSQL 14+ if you prefer Postgres over SQLite

## Setup (Windows PowerShell)

```powershell
cd "C:\Users\Vedaant\Desktop\Inventoru manager"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

On first run, the app will create `inventory.db` automatically.

## Use PostgreSQL instead of SQLite

1) Install PostgreSQL (if not already):
   - Download installer from `https://www.postgresql.org/download/`
   - Note your username, password, and port (default 5432).

2) Create a database (via pgAdmin or psql). Example with `psql`:
```powershell
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE inventory_db;"
```

3) Set `DATABASE_URL` and run the app:
```powershell
$env:DATABASE_URL="postgresql+psycopg2://<USER>:<PASSWORD>@localhost:5432/inventory_db"
python app.py
```

- The app auto-creates tables on startup.
- To switch back to SQLite, unset `DATABASE_URL` or leave it empty.

## Project Structure

```
app.py
requirements.txt
templates/
  base.html
  index.html
static/
  styles.css
inventory.db (created at runtime)
```

## Notes

- This app uses a simple dev secret key; for production, set `FLASK_SECRET_KEY` in your environment.
- To start fresh, stop the app and delete `inventory.db`.

## Next Steps (optional)

- Add user authentication
- Export inventory to CSV
- Add item categories and search/filter
- Add audit logs for adjustments
```



