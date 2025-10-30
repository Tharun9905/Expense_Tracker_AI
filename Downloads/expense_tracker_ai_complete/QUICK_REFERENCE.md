# ⚡ Quick Reference - Essential Commands

## 🎯 Start Application (Choose ONE)

```bash
# Option 1: Automatic (Recommended for Windows)
.\run.ps1

# Option 2: Batch file (Windows)
run.bat

# Option 3: Direct Python (All platforms)
python app.py
```

**✅ Success = Server running on `http://localhost:5000`**

---

## 🔧 Initial Setup (First Time Only)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Optional: Configure email (.env file)
cp .env.template .env
# Edit .env with your email provider

# 3. Optional: Install Tesseract for OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

---

## 🆘 Troubleshooting (Most Common)

| Problem | Solution |
|---------|----------|
| **Port 5000 in use** | Change port in `app.py` or kill process |
| **Module not found** | `pip install -r requirements.txt` |
| **Database error** | Delete `data/expense_tracker.db` and restart |
| **Tesseract error** | Optional - works without it |
| **Email not working** | Skip `.env` setup - app works without email |

---

## 📍 Access Points

| Purpose | URL |
|---------|-----|
| **Home** | http://localhost:5000 |
| **Register** | http://localhost:5000/register |
| **Dashboard** | http://localhost:5000/dashboard |
| **Add Transaction** | http://localhost:5000/add-transaction |
| **Upload Receipt** | http://localhost:5000/upload-receipt |
| **Analytics** | http://localhost:5000/analytics |
| **Budgets** | http://localhost:5000/budgets |

---

## 📋 Verify Installation

```bash
# Check Python version (must be 3.8+)
python --version

# Check Flask installed
pip show flask

# Check all dependencies
pip list
```

---

## 🛑 Stop Application

Press `CTRL+C` in terminal

---

## 📚 Full Documentation

See `TEAM_SETUP_GUIDE.md` for comprehensive guide

---

**Status: ✅ Application Running**  
**Server: http://127.0.0.1:5000**  
**Database: SQLite (auto-created)**