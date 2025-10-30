# Expense Tracker AI - Team Setup & Commands Guide

## 🚀 Quick Start Commands

### **Option 1: Using PowerShell Script (RECOMMENDED - Windows)**
```powershell
.\run.ps1
```
- Automatically checks Python version
- Verifies all dependencies are installed
- Creates data directory if missing
- Starts the Flask application

---

### **Option 2: Using Batch File (Windows)**
```cmd
run.bat
```
- Double-click to run, or execute from Command Prompt
- Same functionality as PowerShell script

---

### **Option 3: Manual Command (All Platforms)**
```bash
python app.py
```
- Works on Windows, macOS, Linux
- Requires manual dependency verification
- Starts Flask server on port 5000

---

## 📋 Initial Setup Commands (First Time Only)

### **1. Install Python (if not installed)**
- **Minimum version required:** Python 3.8+
- **Download from:** https://www.python.org/downloads/
- **Verify installation:**
  ```bash
  python --version
  ```

### **2. Install Required Dependencies**
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- Flask==3.0.0
- Werkzeug==3.0.1
- Pillow==10.1.0
- pytesseract==0.3.10
- Flask-Mail==0.9.1
- python-dotenv==1.0.0

### **3. Optional: Install Tesseract OCR** (for receipt scanning)

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add to system PATH (if not automatic)

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### **4. Environment Configuration (Optional - for email features)**
```bash
# Copy template to actual .env file
cp .env.template .env

# Edit .env with your email provider settings
# Gmail or SendGrid configuration (optional)
```

---

## 🎯 Running the Application

### **Start the Server**
```bash
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### **Access the Application**
- **Local:** http://localhost:5000
- **Network:** http://127.0.0.1:5000 or http://192.168.0.x:5000

### **Stop the Server**
```
Press CTRL+C in the terminal
```

---

## 🔧 Common Operations

### **Troubleshooting: Check Python Installation**
```bash
python --version
pip --version
```

### **Troubleshooting: Check Installed Packages**
```bash
pip list
pip show Flask
pip show pytesseract
```

### **Troubleshooting: Reinstall Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Troubleshooting: Change Server Port**
Edit `app.py` line (around line 400):
```python
app.run(port=5001)  # Change 5000 to any available port
```

### **Reset Database**
```bash
# Delete the database file
del data\expense_tracker.db  # Windows
rm data/expense_tracker.db   # macOS/Linux

# Restart the application to recreate
python app.py
```

---

## 📁 Project Structure for Team

```
expense_tracker_ai/
├── app.py                      # Main Flask application - START HERE
├── requirements.txt            # Python dependencies
├── .env.template              # Environment configuration template
├── run.ps1                    # PowerShell startup script
├── run.bat                    # Windows batch startup script
├── run.sh                     # Linux/macOS startup script
│
├── models/
│   └── database.py            # SQLite database setup and schema
│
├── utils/                     # Core utilities
│   ├── ai_categorizer.py      # AI expense categorization
│   ├── alerts.py              # Budget alerts & anomaly detection
│   ├── analytics.py           # Spending analytics
│   ├── currency_formatter.py  # Currency formatting (INR)
│   ├── email_service.py       # Email notifications
│   ├── enhanced_email_service.py  # Advanced email templates
│   └── ocr_processor.py       # Receipt OCR processing
│
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── dashboard.html        # Main dashboard
│   ├── login.html & register.html  # Authentication
│   ├── add_transaction.html  # Transaction entry
│   ├── upload_receipt.html   # Receipt upload
│   ├── transactions.html     # Transaction history
│   ├── analytics.html        # Analytics & reports
│   └── budgets.html          # Budget management
│
├── static/                    # Frontend assets
│   ├── css/style.css         # Styling
│   ├── js/main.js            # JavaScript functionality
│   └── uploads/              # Receipt uploads storage
│
└── data/
    └── expense_tracker.db    # SQLite database (auto-created)
```

---

## ✨ Key Features Overview

| Feature | Command/Access | Status |
|---------|-----------------|--------|
| **User Authentication** | /login, /register | ✅ Working |
| **Add Transactions** | /add-transaction | ✅ Working |
| **Receipt Upload (OCR)** | /upload-receipt | ✅ Working |
| **AI Categorization** | Auto on expense entry | ✅ Working |
| **Budget Management** | /budgets | ✅ Working |
| **Analytics** | /analytics | ✅ Working |
| **Email Alerts** | Optional (config needed) | ⚙️ Optional |
| **Anomaly Detection** | Automatic | ✅ Working |

---

## 🔐 Security Commands

### **Generate New Secret Key (for production)**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```
Then update `app.py`:
```python
app.config['SECRET_KEY'] = '<generated-key>'
```

### **Password Hashing (used automatically)**
- Werkzeug handles password hashing
- All passwords stored securely with SHA256

---

## 📧 Email Configuration (Optional)

### **For Gmail:**
1. Enable 2-Factor Authentication on Gmail
2. Generate "App Password"
3. Update `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **For SendGrid:**
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### **Test Email:**
- Navigate to `/notifications` in the app
- Click "Send Test Email"

---

## 🐛 Debugging Commands

### **Enable Debug Output**
```bash
set FLASK_DEBUG=1
python app.py
```

### **Check Port Availability**
**Windows:**
```powershell
Get-NetTCPConnection -LocalPort 5000
```

**macOS/Linux:**
```bash
lsof -i :5000
```

### **Kill Process on Port (if stuck)**
**Windows:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :5000
kill -9 <PID>
```

---

## 📝 Team Workflow

### **For Development:**
1. Install Python 3.8+
2. Run `pip install -r requirements.txt`
3. Run `python app.py`
4. Start coding and testing

### **For Deployment:**
1. Update `app.config['SECRET_KEY']` with generated key
2. Configure `.env` for email if needed
3. Use production WSGI server (Gunicorn, uWSGI)
4. Set up SSL/HTTPS

### **For Testing:**
1. Use browser at http://localhost:5000
2. Register test account
3. Add test transactions
4. Verify analytics display
5. Test receipt upload (if Tesseract installed)

---

## ⚡ Performance Tips

- **Database**: SQLite is suitable for small-to-medium use. Use PostgreSQL for production scale.
- **Max Upload Size**: 16MB (configurable in `app.py`)
- **OCR Processing**: First time loading takes ~5-10 seconds
- **Analytics**: Charts render on demand (responsive)

---

## 🆘 FAQ & Quick Fixes

**Q: "ModuleNotFoundError: No module named 'flask'"**
```bash
pip install -r requirements.txt
```

**Q: "Port 5000 already in use"**
```bash
# Change port in app.py or kill existing process (see Debugging section)
```

**Q: "Tesseract not found"**
```bash
# App still works - manual entry of receipt amounts works fine
# Install Tesseract if OCR is needed (see Initial Setup)
```

**Q: "Database locked error"**
```bash
# Stop the server and delete data/expense_tracker.db, then restart
```

**Q: "Email not sending"**
```bash
# Check .env configuration
# Verify SMTP credentials
# Check firewall/antivirus blocking
# App works fine without email - it's optional
```

---

## 📞 Team Communication

- **Setup Issues?** Check the TROUBLESHOOTING section above
- **Database Problems?** Delete `data/expense_tracker.db` and restart
- **Port Conflicts?** Change port in `app.py` (app.run(port=XXXX))
- **Dependencies?** Run `pip install -r requirements.txt` again

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` completed
- [ ] Application starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can register a new account
- [ ] Can add a transaction
- [ ] Analytics page loads
- [ ] Budget page works (optional: email configured)

---

**Last Updated:** 2024
**Status:** Production Ready ✅