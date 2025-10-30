# ⚡ Getting Started in 5 Minutes

**Status:** ✅ Application is running on `http://localhost:5000`

---

## 🚀 QUICKEST START (< 2 minutes)

### Windows Users:
```powershell
.\run.ps1
```

### macOS/Linux Users:
```bash
python app.py
```

**Done! Visit:** `http://localhost:5000`

---

## 📝 First Time Setup (5 minutes)

### Step 1️⃣: Install Python Dependencies (2 min)
```bash
pip install -r requirements.txt
```

### Step 2️⃣: Start the App (30 sec)
```bash
python app.py
```

### Step 3️⃣: Open Browser (30 sec)
```
http://localhost:5000
```

### Step 4️⃣: Create Account (1 min)
- Click "Register"
- Enter: Username, Email, Password
- Click "Register"

### Step 5️⃣: Login & Explore (1 min)
- Login with your credentials
- Click "Add Transaction"
- Add a sample expense
- Check Analytics page

**✅ Done in ~5 minutes!**

---

## 🎯 Most Important Commands

| Task | Command |
|------|---------|
| **Start App** | `python app.py` or `.\run.ps1` |
| **Install Dependencies** | `pip install -r requirements.txt` |
| **Stop App** | Press `CTRL+C` |
| **Access App** | `http://localhost:5000` |
| **Reset Database** | Delete `data/expense_tracker.db` then restart |

---

## 🔍 Troubleshooting (If Something Goes Wrong)

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | `pip install -r requirements.txt` |
| Page not loading | Restart: Stop (CTRL+C), then `python app.py` |
| "Port 5000 already in use" | Change port in `app.py` line ~400: `app.run(port=5001)` |
| Database error | Delete `data/expense_tracker.db` and restart |

---

## 🌟 Features to Try

1. **Register** - Create a free account
2. **Add Transaction** - Log an expense or income
3. **View Dashboard** - See your balance
4. **Analytics** - View spending charts
5. **Upload Receipt** - Scan a receipt image (OCR)
6. **Budgets** - Set spending limits
7. **Transactions** - View all history

---

## 📋 What You Need

- ✅ Python 3.8+
- ✅ pip (comes with Python)
- ✅ Project files (you have them!)
- ⚙️ Optional: Tesseract (for receipt scanning)

---

## ✅ Verify It Works

1. Run `python app.py`
2. See message: `Running on http://127.0.0.1:5000`
3. Open browser to `http://localhost:5000`
4. See "Expense Tracker AI" heading
5. Success! ✅

---

## 📚 Need More Details?

- **Full Setup:** `TEAM_SETUP_GUIDE.md`
- **All Commands:** `COMMANDS_SUMMARY.md`
- **Quick Ref:** `QUICK_REFERENCE.md`
- **Flowchart:** `SETUP_FLOWCHART.md`

---

## 💡 Pro Tips

- Email setup is **optional** - app works without it
- Tesseract OCR is **optional** - manual entry works fine
- Database created automatically on first run
- No additional configuration needed for basic use
- Perfect for learning Flask + SQLite!

---

**You're ready! Happy coding! 🚀**