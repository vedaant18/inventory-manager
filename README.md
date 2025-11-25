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

## Production Deployment

### 🚀 Deploy to AWS with Custom Domain and HTTPS

**Have a domain name? Ready to deploy?**

#### Step 1: Push to GitHub (5 minutes)
👉 **[GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md)** - Push your code to GitHub

#### Step 2: Deploy to AWS (2-3 hours)
👉 **[START_HERE.md](START_HERE.md)** - Complete AWS deployment guide

This will get you from code to live HTTPS site!

### Deployment Guides

1. **[GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md)** - 🐙 Push to GitHub in 5 minutes
2. **[START_HERE.md](START_HERE.md)** - 🌟 Main AWS deployment guide
3. **[DOMAIN_WITHOUT_ROUTE53.md](DOMAIN_WITHOUT_ROUTE53.md)** - 🌐 Setup domain without Route 53 (save $0.50/mo)
4. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ Quick commands and troubleshooting
5. **[GIT_WORKFLOW.md](GIT_WORKFLOW.md)** - 🔄 Daily Git workflow and best practices
6. **[GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)** - 📖 Detailed GitHub workflow
7. **[AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)** - 📖 Detailed AWS documentation
8. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - ✅ Task checklist and monitoring
9. **[DEPLOYMENT_ROADMAP.md](DEPLOYMENT_ROADMAP.md)** - 🗺️ Visual deployment roadmap
10. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 🏗️ System architecture and scaling
11. **[deployment_configs/](deployment_configs/)** - 🛠️ Ready-to-use configuration files

### Quick Start

```powershell
# 1. Generate production secret key
python generate_secret_key.py

# 2. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/inventory-manager.git
git push -u origin main

# 3. Follow START_HERE.md to deploy to AWS
```

### What You'll Get

- ✅ Custom domain (yourdomain.com)
- ✅ HTTPS with green padlock 🔒
- ✅ Production-ready server
- ✅ Auto-renewing SSL certificates
- ✅ Easy updates with `git pull`

### Costs

- **First year**: ~$1.50/month (AWS free tier)
- **After**: ~$10/month (EC2 + Route 53)
- **SSL**: FREE forever (Let's Encrypt)

## Next Steps (optional)

- Add user authentication
- Export inventory to CSV
- Add audit logs for adjustments
- Set up automated backups
- Configure monitoring with CloudWatch
```



