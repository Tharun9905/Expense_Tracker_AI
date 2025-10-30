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

### Fresh Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tharun9905/Expense_Tracker_AI.git
   cd Expense_Tracker_AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the template file
   cp .env.template .env
   
   # Edit .env with your email configuration (optional)
   # The app works without email configuration
   ```

4. **Run the application**
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
Expense_Tracker_AI/
│
├── app.py                        # Main Flask application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .env.template                 # Environment variables template
├── .gitignore                    # Git ignore rules
├── run.bat, run.ps1, run.sh      # Startup scripts
│
├── models/
│   ├── __init__.py
│   └── database.py              # Database setup and models
│
├── utils/
│   ├── __init__.py
│   ├── ai_categorizer.py        # AI-powered expense categorization
│   ├── alerts.py                # Budget alerts and anomaly detection
│   ├── analytics.py             # Spending analytics and reports
│   ├── currency_formatter.py    # Currency formatting utilities
│   ├── email_service.py         # Email notification service
│   ├── enhanced_email_service.py # Advanced email templates
│   └── ocr_processor.py         # Receipt OCR processing
│
├── templates/                    # HTML templates
│   ├── base.html                # Base template with navigation
│   ├── index.html               # Landing page
│   ├── login.html               # User login
│   ├── register.html            # User registration
│   ├── dashboard.html           # Main dashboard
│   ├── add_transaction.html     # Add transactions
│   ├── upload_receipt.html      # Receipt upload
│   ├── transactions.html        # Transaction history
│   ├── analytics.html           # Analytics and reports
│   ├── budgets.html             # Budget management
│   └── notifications.html       # Email notification settings
│
├── static/                       # Static assets
│   ├── css/style.css            # Application styles
│   ├── js/main.js               # JavaScript functionality
│   └── uploads/.gitkeep         # Receipt uploads directory
│
└── data/
    └── expense_tracker.db       # SQLite database (auto-created)
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

## Email Configuration (Optional)

The application includes email notification features that are **completely optional**. The app works perfectly without email configuration.

### To Enable Email Notifications:

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Choose your email provider and update .env:**

   **For Gmail:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

   **For SendGrid:**
   ```
   SMTP_SERVER=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   ```

3. **Test email functionality in the app's Notifications page**

**Note:** All features work without email configuration. Email is only for budget alerts and daily summaries.

## Troubleshooting

**Issue: Tesseract not found**
**Solution:** Install Tesseract OCR and add to PATH, or use the app without OCR (manual entry works fine)

**Issue: Database errors**
**Solution:** Delete `data/expense_tracker.db` and restart

**Issue: Port already in use**
**Solution:** Change port in `app.py`: `app.run(port=5001)`

**Issue: Email not working**
**Solution:** Check .env configuration or disable email features - the app works perfectly without them

## Credits

Developed for AI & Data Science project - Phase II Review

---

**Happy Expense Tracking! 💸📊**
