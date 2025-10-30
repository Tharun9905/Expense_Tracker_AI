# 🚀 Project Setup Flowchart

## Starting the Application - Decision Tree

```
START
  │
  ├─► Windows User?
  │    ├─► YES ─► Use PowerShell? 
  │    │           ├─► YES ─► Run: .\run.ps1 ─────────────┐
  │    │           └─► NO ──► Run: run.bat ───────────────┤
  │    │                                                    │
  │    └─► NO ──► macOS/Linux? 
  │             └─► YES ─► Run: bash run.sh ──────────────┤
  │                                                         │
  │     OR (Any platform)                                  │
  │     Run directly: python app.py ──────────────────────┤
  │                                                        │
  └────────────────────────────────────────────────────────┤
                                                            │
   ✅ Server starts:                                       │
       * Running on http://127.0.0.1:5000 ◄──────────────┘
       * Press CTRL+C to stop
```

---

## First Time Setup - Step by Step

```
┌─────────────────────────────────────────────────────────────┐
│                    FIRST TIME SETUP                         │
├─────────────────────────────────────────────────────────────┤

STEP 1: Install Python
└─► Minimum: Python 3.8+
    Verify: python --version

STEP 2: Install Dependencies
└─► Command: pip install -r requirements.txt
    Packages:
    • Flask==3.0.0
    • Werkzeug==3.0.1
    • Pillow==10.1.0
    • pytesseract==0.3.10
    • Flask-Mail==0.9.1
    • python-dotenv==1.0.0

STEP 3: Optional - Setup Email (for alerts)
└─► Copy: cp .env.template .env
    Edit: .env with your SMTP settings
    (Gmail, SendGrid, or other)
    Skip: App works 100% without this

STEP 4: Optional - Install Tesseract OCR
└─► Windows: Download installer from GitHub
    macOS: brew install tesseract
    Linux: sudo apt-get install tesseract-ocr
    Skip: App works with manual entry

STEP 5: Start Application
└─► Command: python app.py
    OR: .\run.ps1 (Windows)
    OR: run.bat (Windows)

STEP 6: Access Application
└─► Browser: http://localhost:5000
    Register: Create account
    Use: Start tracking expenses!
```

---

## Quick Command Reference Card

```
┌────────────────────────────────────────────────┐
│        MOST USED COMMANDS (Copy & Paste)       │
├────────────────────────────────────────────────┤

🚀 START APPLICATION
─────────────────────
Windows (PowerShell):
  .\run.ps1

Windows (Command Prompt):
  run.bat

Mac / Linux:
  python app.py

All platforms:
  python app.py


⚙️ SETUP & VERIFICATION
─────────────────────
Check Python:
  python --version

Install dependencies:
  pip install -r requirements.txt

Check if Flask installed:
  pip show flask

List all packages:
  pip list


🛑 STOP & TROUBLESHOOT
─────────────────────
Stop server:
  Press CTRL+C

Reinstall everything:
  pip install -r requirements.txt --force-reinstall

Check port 5000:
  # Windows PowerShell
  Get-NetTCPConnection -LocalPort 5000

Reset database:
  del data\expense_tracker.db
  # Then restart app.py


📧 EMAIL SETUP (Optional)
─────────────────────────
Create .env file:
  cp .env.template .env

Edit and add:
  SMTP_SERVER=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=your-app-password
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYERS                        │
├─────────────────────────────────────────────────────────────┤

FRONTEND (Web Browser)
│
├── Templates (HTML/CSS/JS)
│   ├── dashboard.html
│   ├── transactions.html
│   ├── analytics.html
│   └── budgets.html
│
BACKEND (Flask Server - :5000)
│
├── app.py (Main Application)
│   ├── Routes
│   ├── Session Management
│   └── File Upload Handler
│
├── Utils (Business Logic)
│   ├── ai_categorizer.py (AI)
│   ├── ocr_processor.py (Receipts)
│   ├── alerts.py (Budgets)
│   ├── analytics.py (Reports)
│   └── email_service.py (Notifications)
│
├── Models (Database)
│   └── database.py (SQLite)
│
DATABASE
│
└── data/expense_tracker.db (SQLite)
```

---

## File Structure for Quick Navigation

```
expense_tracker_ai/
│
├── 🚀 STARTUP
│   ├── run.ps1 ..................... PowerShell startup script
│   ├── run.bat ..................... Batch startup script
│   └── app.py ...................... Main application (200+ lines)
│
├── 📦 DEPENDENCIES
│   └── requirements.txt ............ All pip packages
│
├── ⚙️ CONFIGURATION
│   ├── .env.template .............. Email config template
│   └── .env ........................ (created by you)
│
├── 💾 DATABASE
│   ├── models/
│   │   └── database.py ............ Database schema & connection
│   └── data/
│       └── expense_tracker.db ..... SQLite file (auto-created)
│
├── 🧠 UTILITIES
│   ├── utils/ai_categorizer.py .... AI expense categorization
│   ├── utils/ocr_processor.py ..... Receipt scanning
│   ├── utils/alerts.py ........... Budget alerts & anomalies
│   ├── utils/analytics.py ........ Reports & charts
│   ├── utils/email_service.py .... Email notifications
│   └── utils/currency_formatter.py. INR formatting
│
├── 🎨 FRONTEND
│   ├── templates/
│   │   ├── base.html ............. Main layout
│   │   ├── dashboard.html ........ Home page
│   │   ├── add_transaction.html .. Transaction entry
│   │   ├── upload_receipt.html ... Receipt upload
│   │   ├── analytics.html ........ Charts & reports
│   │   └── budgets.html ......... Budget management
│   └── static/
│       ├── css/style.css ........ Styling
│       ├── js/main.js ........... JavaScript
│       └── uploads/ ............ User file storage
│
└── 📚 DOCUMENTATION
    ├── README.md ................. Full documentation
    ├── TEAM_SETUP_GUIDE.md ....... This comprehensive guide
    ├── QUICK_REFERENCE.md ....... Quick commands
    └── SETUP_FLOWCHART.md ....... This file
```

---

## Port & Network Information

```
┌──────────────────────────────────────────────┐
│         HOW TO ACCESS THE APPLICATION        │
├──────────────────────────────────────────────┤

LOCAL ACCESS:
├─ http://localhost:5000
├─ http://127.0.0.1:5000
└─ http://0.0.0.0:5000

NETWORK ACCESS (Same WiFi):
├─ http://192.168.0.105:5000 (or your IP)
├─ Use ipconfig (Windows) or ifconfig (Mac/Linux)
└─ to find your local IP address

DEFAULT PORT: 5000
├─ Can be changed in app.py
└─ Change line: app.run(port=5001)

FIREWALL CONSIDERATIONS:
├─ Windows Firewall may block port 5000
├─ Add exception if needed
└─ Or change to port 8000/3000 (common ports)
```

---

## Troubleshooting Decision Tree

```
❌ APPLICATION NOT STARTING?
│
├─► Does terminal show error message?
│   ├─► "ModuleNotFoundError"
│   │   └─► RUN: pip install -r requirements.txt
│   │
│   ├─► "Port 5000 in use"
│   │   └─► EITHER: Kill existing process (see below)
│   │       OR: Change port in app.py
│   │
│   ├─► "Permission denied"
│   │   └─► Check file permissions or run as admin
│   │
│   └─► "Other error"
│       └─► Check TEAM_SETUP_GUIDE.md for details
│
├─► Port already in use?
│   ├─► Windows: netstat -ano | findstr :5000
│   ├─► Mac/Linux: lsof -i :5000
│   └─► Kill: taskkill /PID <PID> /F (Windows)
│
└─► Still not working?
    └─► Delete: data/expense_tracker.db
        Restart: python app.py
        (Database will auto-recreate)
```

---

## Success Checklist

```
✅ VERIFY INSTALLATION

After running the application, check:

□ Server message shows "Running on http://127.0.0.1:5000"
□ Can access http://localhost:5000 in browser
□ Page loads and shows "Expense Tracker AI" heading
□ Can click "Register"
□ Can enter username, email, password
□ Registration successful and redirects to login
□ Can login with created credentials
□ Dashboard shows empty transaction list
□ Can navigate to different pages without errors
□ Add Transaction page has dropdown for categories
□ Analytics page loads (may show empty charts)
□ Budgets page shows option to add budget

If ALL checks pass: ✅ SETUP COMPLETE!
```

---

## Performance Tips

```
📊 OPTIMIZATION GUIDELINES

Database:
• SQLite used (good for development/small scale)
• Consider PostgreSQL for production (100+ users)
• Database file: data/expense_tracker.db (~few MB)

Upload Limits:
• Max file size: 16 MB per upload
• Supported: PNG, JPG, JPEG, GIF, PDF
• Location: static/uploads/

Memory:
• Flask development server: ~80 MB RAM
• OCR processing: ~200 MB (Tesseract optional)
• Typical session: minimal

Performance Metrics:
• Page load: < 500ms
• Transaction add: < 200ms
• Analytics generation: 1-3s (depending on data)
• OCR processing: 5-10s (first time)
```

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** ✅ Ready for Team