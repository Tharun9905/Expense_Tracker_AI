# Expense Tracker AI 🤖💰

A comprehensive expense tracking web application with AI-powered categorization, OCR receipt scanning, smart budget alerts, and data visualization.

## Features

✨ **Core Functionalities:**
- User authentication (Register, Login, Logout)
- Add income and expense transactions
- Upload receipt images with OCR extraction
- AI-powered automatic expense categorization
- Smart budget management with alerts
- Real-time spending analytics and visualizations
- Anomaly detection for unusual spending patterns
- Interactive charts and dashboards
- Filter and search transactions

## Technology Stack

- **Backend:** Flask (Python 3.8+)
- **Database:** SQLite3
- **Frontend:** Bootstrap 5, Chart.js
- **AI/ML:** Custom categorization algorithm
- **OCR:** Tesseract OCR, Pillow
- **Authentication:** Werkzeug security

## Installation & Setup

### Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Tesseract OCR** installed (optional - app works without it with fallback functionality):
   - **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`

### Quick Start (Ready to Run!)

The application is **FULLY CONFIGURED** and ready to run! All dependencies are pre-installed.

#### Option 1: Using PowerShell Script (Recommended)
1. **Open PowerShell in the project directory**
2. **Run the startup script:**
   ```powershell
   .\run.ps1
   ```

#### Option 2: Using Batch File
1. **Double-click `run.bat`** or run from command prompt:
   ```cmd
   run.bat
   ```

#### Option 3: Manual Start
1. **Open terminal/command prompt in project directory**
2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

### Fresh Installation (if needed)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

## Usage Guide

### 1. Register & Login
- Create a new account with username, email, and password
- Login with your credentials

### 2. Add Transactions
- Click "Add Transaction" in the navigation
- Choose type (Income/Expense)
- Enter amount, category, description, and date
- Select "Auto-Detect (AI)" for automatic categorization

### 3. Upload Receipts
- Click "Upload Receipt"
- Upload a receipt image (JPG, PNG, PDF)
- The system will automatically extract amount and date using OCR
- Categorize the expense using AI

### 4. View Analytics
- Navigate to "Analytics" page
- View spending trends, category breakdowns
- Filter by week, month, or year

### 5. Set Budgets
- Go to "Budgets" page
- Set budget limits for different categories
- Receive alerts when approaching or exceeding limits

## Project Structure

```
expense_tracker_ai/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── models/
│   └── database.py            # Database setup
│
├── utils/
│   ├── ocr_processor.py       # Receipt OCR
│   ├── ai_categorizer.py      # AI categorization
│   ├── alerts.py              # Budget alerts
│   └── analytics.py           # Analytics
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── upload_receipt.html
│   ├── transactions.html
│   ├── analytics.html
│   └── budgets.html
│
├── static/                     # Static files
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/               # Receipt uploads
│
└── data/
    └── expense_tracker.db     # SQLite database
```

## Features Included from PPT

✅ User Registration & Authentication
✅ Income & Expense Tracking
✅ Receipt Upload with OCR (Tesseract)
✅ AI-Powered Categorization
✅ Smart Budget Alerts
✅ Spending Analysis & Visualizations
✅ Interactive Charts (Chart.js)
✅ Dashboard with Overview
✅ Transaction Filtering
✅ Anomaly Detection
✅ Category-wise Breakdown
✅ Date-based Analytics

## Troubleshooting

**Issue: Tesseract not found**
**Solution:** Install Tesseract OCR and add to PATH

**Issue: Database errors**
**Solution:** Delete `data/expense_tracker.db` and restart

**Issue: Port already in use**
**Solution:** Change port in `app.py`: `app.run(port=5001)`

## Credits

Developed for AI & Data Science project - Phase II Review

---

**Happy Expense Tracking! 💸📊**
