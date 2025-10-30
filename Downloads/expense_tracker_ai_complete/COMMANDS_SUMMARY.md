# 📋 Complete Commands Summary for Project Team

## 🎯 Summary: Application Successfully Running ✅

**Current Status:** Flask server is running on `http://127.0.0.1:5000`

---

## 🚀 SECTION 1: STARTING THE APPLICATION

### **Start Application - 3 Methods**

#### Method 1: PowerShell (Windows - RECOMMENDED)
```powershell
.\run.ps1
```
- Checks Python installation
- Verifies dependencies
- Creates data folder if needed
- Starts Flask server

#### Method 2: Batch File (Windows)
```cmd
run.bat
```
- Double-click or run from Command Prompt
- Automated startup script

#### Method 3: Direct Python (All Platforms)
```bash
python app.py
```
- Manual startup
- Works on Windows, macOS, Linux

### **Expected Output**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.105:5000
 * Press CTRL+C to quit
```

### **Stop Application**
```
Press CTRL+C in terminal
```

---

## 🔧 SECTION 2: INITIAL SETUP COMMANDS

### **2.1 Verify Python Installation**
```bash
python --version
```
**Required:** Python 3.8 or higher

### **2.2 Verify pip Installation**
```bash
pip --version
```

### **2.3 Install Project Dependencies**
```bash
pip install -r requirements.txt
```

**Packages Installed:**
- Flask==3.0.0
- Werkzeug==3.0.1
- Pillow==10.1.0
- pytesseract==0.3.10
- Flask-Mail==0.9.1
- python-dotenv==1.0.0

### **2.4 Check Installed Packages**
```bash
pip list
```

### **2.5 Verify Specific Package**
```bash
pip show flask
pip show werkzeug
pip show pillow
pip show pytesseract
```

### **2.6 Upgrade pip (Recommended)**
```bash
pip install --upgrade pip
```

### **2.7 Reinstall All Dependencies**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📧 SECTION 3: EMAIL CONFIGURATION (Optional)

### **3.1 Create Environment File from Template**
```bash
# Windows
copy .env.template .env

# macOS/Linux
cp .env.template .env
```

### **3.2 Gmail Configuration**

**Step 1: Get Gmail App Password**
- Enable 2-Factor Authentication on Gmail
- Generate App-specific password
- Copy the 16-character password

**Step 2: Update .env file**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=True
SMTP_SENDER_NAME=Expense Tracker
SMTP_SENDER_EMAIL=your-email@gmail.com
```

### **3.3 SendGrid Configuration**

**Step 1: Get SendGrid API Key**
- Create SendGrid account
- Generate API key

**Step 2: Update .env file**
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_SENDER_NAME=Expense Tracker
SMTP_SENDER_EMAIL=your-email@sendgrid.com
```

### **3.4 Test Email Configuration**
1. Start the application: `python app.py`
2. Navigate to: `http://localhost:5000/notifications`
3. Click "Send Test Email"
4. Check inbox (or spam folder)

### **3.5 Disable Email Notifications**
Edit `.env`:
```
ENABLE_EMAIL_NOTIFICATIONS=False
```

---

## 🖥️ SECTION 4: OCR/TESSERACT SETUP (Optional)

### **4.1 Install Tesseract - Windows**
```
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Accept default installation path
4. Add to system PATH if prompted
```

### **4.2 Install Tesseract - macOS**
```bash
brew install tesseract
```

### **4.3 Install Tesseract - Linux (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### **4.4 Verify Tesseract Installation**
```bash
tesseract --version
```

### **Note on Tesseract**
- Optional feature
- App works 100% without it
- Users can manually enter receipt amounts
- Receipt upload page has fallback UI

---

## 💾 SECTION 5: DATABASE OPERATIONS

### **5.1 Database Location**
```
data/expense_tracker.db
```

### **5.2 Database Auto-Creation**
- Automatically created on first run
- SQLite format
- Located in `data/` folder

### **5.3 Reset Database**
```bash
# Windows
del data\expense_tracker.db

# macOS/Linux
rm data/expense_tracker.db
```
**Then restart:** `python app.py`

### **5.4 Backup Database**
```bash
# Windows
copy data\expense_tracker.db data\expense_tracker.db.backup

# macOS/Linux
cp data/expense_tracker.db data/expense_tracker.db.backup
```

### **5.5 Restore Database**
```bash
# Windows
copy data\expense_tracker.db.backup data\expense_tracker.db

# macOS/Linux
cp data/expense_tracker.db.backup data/expense_tracker.db
```

---

## 🔐 SECTION 6: SECURITY COMMANDS

### **6.1 Generate Secure Secret Key**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### **6.2 Update Secret Key in app.py**
```python
app.config['SECRET_KEY'] = 'generated-secret-key-from-above'
```

### **6.3 Hash a Password (for testing)**
```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
```

### **6.4 Verify Password Hash**
```bash
python -c "from werkzeug.security import check_password_hash; print(check_password_hash('hash_here', 'password_here'))"
```

---

## 🐛 SECTION 7: DEBUGGING & TROUBLESHOOTING

### **7.1 Enable Debug Mode**
```bash
# Windows
set FLASK_DEBUG=1
python app.py

# macOS/Linux
export FLASK_DEBUG=1
python app.py
```

### **7.2 Check Port Status**

**Windows (PowerShell):**
```powershell
Get-NetTCPConnection -LocalPort 5000
```

**Windows (Command Prompt):**
```cmd
netstat -ano | findstr :5000
```

**macOS/Linux:**
```bash
lsof -i :5000
```

### **7.3 Kill Process on Port 5000**

**Windows (PowerShell):**
```powershell
Stop-Process -Id <PID> -Force
```

**Windows (Command Prompt):**
```cmd
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
kill -9 <PID>
```

### **7.4 Change Application Port**

Edit `app.py` (find the last line):
```python
# Change from:
app.run()

# To:
app.run(port=5001)
```

### **7.5 Run on Different Port Directly**
```bash
python -c "from app import app; app.run(port=8000)"
```

### **7.6 Check All Network Connections**
```powershell
# Windows
Get-NetTCPConnection

# macOS/Linux
netstat -tuln
```

---

## 📊 SECTION 8: VERIFICATION COMMANDS

### **8.1 Verify Python Version**
```bash
python --version
```
**Expected:** Python 3.8.x or higher

### **8.2 Verify All Dependencies**
```bash
pip list
```

### **8.3 Check Flask Installation**
```bash
python -c "import flask; print(flask.__version__)"
```

### **8.4 Check Flask App Imports**
```bash
python -c "from app import app; print('App loaded successfully')"
```

### **8.5 List All Installed Packages with Details**
```bash
pip freeze
```

### **8.6 Create Requirements from Current Environment**
```bash
pip freeze > requirements_current.txt
```

---

## 🌐 SECTION 9: ACCESS POINTS & URLS

### **Local Access**
```
http://localhost:5000
http://127.0.0.1:5000
http://0.0.0.0:5000
```

### **Network Access (Same WiFi)**
```
http://<your-ip>:5000
# Example: http://192.168.0.105:5000
```

### **Get Your Local IP Address**

**Windows (PowerShell):**
```powershell
ipconfig
# Look for "IPv4 Address"
```

**Windows (Command Prompt):**
```cmd
ipconfig
```

**macOS/Linux:**
```bash
ifconfig
# or
ip addr show
```

### **Application Routes**
```
/                  - Home page / Landing page
/register          - User registration
/login             - User login
/logout            - User logout
/dashboard         - Main dashboard
/add-transaction   - Add income/expense
/upload-receipt    - Upload receipt image
/transactions      - View all transactions
/analytics         - View analytics & charts
/budgets           - Manage budgets
/notifications     - Email notification settings
/api/...           - API endpoints
```

---

## 🚨 SECTION 10: COMMON ERRORS & SOLUTIONS

### **Error: "ModuleNotFoundError: No module named 'flask'"**
```bash
pip install -r requirements.txt
```

### **Error: "Port 5000 already in use"**
```bash
# Option 1: Use different port
python -c "from app import app; app.run(port=5001)"

# Option 2: Kill existing process (see Section 7.3)
```

### **Error: "TemplateNotFound"**
```bash
# Verify templates directory exists
# Project structure should be: /templates/*.html
# Make sure you're running from project root
```

### **Error: "pytesseract not found"**
```bash
# Option 1: Install it
pip install pytesseract

# Option 2: It's optional - app still works without it
# Just skip receipt OCR functionality
```

### **Error: "Database is locked"**
```bash
# Stop the app and delete database
del data/expense_tracker.db
# Restart app.py
```

### **Error: "werkzeug.security error"**
```bash
pip install --upgrade werkzeug
```

### **Error: "No module named 'dotenv'"**
```bash
pip install python-dotenv
```

---

## 📁 SECTION 11: PROJECT STRUCTURE NAVIGATION

### **Navigate to Project Directory**

**Windows (PowerShell):**
```powershell
Set-Location "c:\Users\THARUN\Downloads\expense_tracker_ai_complete\expense_tracker_ai"
```

**Windows (Command Prompt):**
```cmd
cd c:\Users\THARUN\Downloads\expense_tracker_ai_complete\expense_tracker_ai
```

**macOS/Linux:**
```bash
cd /path/to/expense_tracker_ai
```

### **View Project Structure**

**Windows:**
```cmd
tree /F
```

**macOS/Linux:**
```bash
find . -type f -name "*.py" | head -20
```

### **List Python Files**
```bash
# Windows
dir *.py
dir utils\*.py

# macOS/Linux
ls *.py
ls utils/*.py
```

---

## ⚡ SECTION 12: PERFORMANCE OPTIMIZATION

### **Run on Production Server**

**Using Gunicorn (recommended):**
```bash
# Install
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Using uWSGI:**
```bash
# Install
pip install uwsgi

# Run
uwsgi --http :5000 --wsgi-file app.py --callable app
```

### **Increase Worker Threads**
```bash
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

### **Enable Logging**
```bash
gunicorn --log-level debug -b 0.0.0.0:5000 app:app
```

---

## 📚 SECTION 13: QUICK COPY-PASTE COMMANDS

### **Complete First-Time Setup**
```bash
# Step 1: Navigate to project
cd expense_tracker_ai

# Step 2: Install Python dependencies
pip install -r requirements.txt

# Step 3: Run application
python app.py
```

### **Fresh Start (Database Reset)**
```bash
# Delete database
del data\expense_tracker.db

# Restart application
python app.py
```

### **Complete Environment Setup with Email**
```bash
# Install dependencies
pip install -r requirements.txt

# Create email config
copy .env.template .env

# Edit .env with your details
# Then run
python app.py
```

### **Development Mode (with debugging)**
```bash
set FLASK_DEBUG=1
python app.py
```

### **Production Mode**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🎓 SECTION 14: TEAM GUIDELINES

### **For Developers**
1. Clone/download project
2. Run: `pip install -r requirements.txt`
3. Run: `python app.py`
4. Start coding!

### **For Testers**
1. Start application: `python app.py`
2. Access: `http://localhost:5000`
3. Test all features
4. Report bugs with screenshots

### **For Deployment**
1. Update `SECRET_KEY` in app.py
2. Configure .env for email (optional)
3. Use Gunicorn for production
4. Set up SSL/HTTPS
5. Configure firewall

### **For Database Maintenance**
1. Backup regularly: `cp data/expense_tracker.db data/expense_tracker.db.backup`
2. Check size: Monitor for growth
3. Migrate if needed: PostgreSQL for scale
4. Clean old data: As per policy

---

## ✅ FINAL CHECKLIST

```
VERIFICATION CHECKLIST:

□ Python 3.8+ installed
□ pip works properly
□ All dependencies installed (pip list shows all)
□ Application starts (no error in terminal)
□ Server shows "Running on http://127.0.0.1:5000"
□ Can access http://localhost:5000 in browser
□ Can register new user
□ Can login with credentials
□ Dashboard displays
□ Can add transaction
□ Analytics loads
□ No console errors

ALL ✅ = READY FOR TEAM!
```

---

## 📞 SUPPORT

**Quick Links:**
- Full Setup Guide: `TEAM_SETUP_GUIDE.md`
- Quick Reference: `QUICK_REFERENCE.md`
- Flowchart: `SETUP_FLOWCHART.md`
- README: `README.md`

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** ✅ Complete and Ready for Team Distribution