# 🔄 Alert System Flow Diagram

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPENSE TRACKER APPLICATION                  │
└─────────────────────────────────────────────────────────────────┘

          ┌─────────────────────────────────────────┐
          │     User Adds Transaction or           │
          │     Uploads Receipt                    │
          └──────────────────┬──────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ add_transaction()│
                    │  upload_receipt()│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Save to Database│
                    └────────┬────────┘
                             │
                    ┌────────▼─────────┐
                    │ Redirect to      │
                    │ Dashboard        │
                    └────────┬─────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │   dashboard() Route Called          │
          └──────────────────┬──────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────────┐  ┌──────▼──────────┐  ┌─────▼──────────────┐
   │ Fetch Recent │  │ Get Category    │  │ Check Alerts       │
   │ Transactions │  │ Breakdown       │  │ ← ALERT SYSTEM     │
   └────┬─────────┘  └──────┬──────────┘  └─────┬──────────────┘
        │                   │                   │
        │                   │          ┌────────▼────────┐
        │                   │          │check_budget_    │
        │                   │          │alerts(user_id)  │
        │                   │          └────────┬────────┘
        │                   │                   │
        │                   │          ┌────────▼────────┐
        │                   │          │detect_anomalies │
        │                   │          │(user_id)        │
        │                   │          └────────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │  Render Dashboard   │
                 │  with all info      │
                 └─────────────────────┘
```

---

## Detailed Alert Checking Flow

### When `check_budget_alerts(user_id)` is called:

```
check_budget_alerts(user_id)
│
├─ Get all budgets for user
│
└─ FOR EACH BUDGET:
   │
   ├─ Calculate: Spent Amount for this month
   │
   ├─ Calculate: Percentage = (Spent / Budget Amount) * 100
   │
   └─ IF Percentage >= 80%:
      │
      ├─ Create alert message
      ├─ Add to alerts[] list (for dashboard display)
      │
      ├─ *** KEY: Check if already sent today ***
      │   │
      │   ├─ has_alert_been_sent_today(
      │   │    user_id, 
      │   │    'budget_warning', 
      │   │    category_name
      │   │ )
      │   │
      │   ├─ Query: SELECT id FROM email_alert_history
      │   │         WHERE user_id = ?
      │   │         AND alert_type = 'budget_warning'
      │   │         AND category = ?
      │   │         AND sent_date = TODAY
      │   │
      │   └─ Result: True or False
      │
      ├─ IF result = TRUE (already sent today):
      │  └─ SKIP - Don't send email again
      │
      ├─ IF result = FALSE (not sent today):
      │  │
      │  ├─ Add to alerts_to_send[] list
      │  │
      │  ├─ record_alert_sent(
      │  │    user_id, 
      │  │    'budget_warning', 
      │  │    category_name
      │  │ )
      │  │
      │  └─ INSERT INTO email_alert_history
      │     (user_id, alert_type, category, sent_date, created_at)
      │     VALUES (?, 'budget_warning', ?, TODAY, NOW())
      │
      └─ IF Percentage >= 100%:
         └─ SAME PROCESS but with 'budget_danger' type
         │
         └─ Note: 'budget_danger' and 'budget_warning' are separate
            so can send both emails on same day if needed
│
├─ IF alerts_to_send[] is NOT empty:
│  │
│  ├─ send_budget_alert_email(user_id, alerts_to_send)
│  │
│  └─ PRINT: "✅ Budget alert email sent for X category/categories"
│
├─ ELSE (alerts_to_send[] is empty):
│  │
│  └─ PRINT: "📧 Budget alert already sent today for all triggered categories"
│
└─ RETURN alerts[] (not alerts_to_send!)
   └─ Original alerts list for dashboard display
```

---

## Anomaly Detection Flow

### When `detect_anomalies(user_id)` is called:

```
detect_anomalies(user_id)
│
├─ Get average spending per category (last 30 days)
│
├─ Get unusual transactions (last 7 days, > 2x average)
│
└─ FOR EACH UNUSUAL TRANSACTION:
   │
   ├─ Create anomaly message
   ├─ Add to anomalies[] list (for dashboard display)
   │
   ├─ *** KEY: Check if already sent today ***
   │   │
   │   ├─ has_alert_been_sent_today(
   │   │    user_id, 
   │   │    'anomaly', 
   │   │    category_name
   │   │ )
   │   │
   │   └─ Result: True or False
   │
   ├─ IF result = TRUE (already sent today):
   │  └─ SKIP - Don't send email again
   │
   ├─ IF result = FALSE (not sent today):
   │  │
   │  ├─ Add to anomalies_to_send[] list
   │  │
   │  ├─ record_alert_sent(
   │  │    user_id, 
   │  │    'anomaly', 
   │  │    category_name
   │  │ )
   │  │
   │  └─ INSERT INTO email_alert_history
      │     (user_id, alert_type, category, sent_date, created_at)
      │     VALUES (?, 'anomaly', ?, TODAY, NOW())
   │
├─ IF anomalies_to_send[] is NOT empty:
│  │
│  ├─ send_anomaly_alert_email(user_id, anomalies_to_send)
│  │
│  └─ PRINT: "✅ Anomaly alert email sent for X anomaly/anomalies"
│
├─ ELSE (anomalies_to_send[] is empty):
│  │
│  └─ PRINT: "📧 Anomaly alert already sent today for this category"
│
└─ RETURN anomalies[] (not anomalies_to_send!)
   └─ Original anomalies list for dashboard display
```

---

## Complete Transaction Flow With Email Deduplication

```
TIME: 10:00 AM
═════════════════════════════════════════════════════════════════════
User uploads receipt: Restaurant - $200 (Budget: $500)
│
├─ Transaction saved to database
├─ Dashboard loaded
├─ check_budget_alerts() called
│  │
│  ├─ Spending: $200 (40% of $500)
│  ├─ 40% < 80% threshold
│  └─ No alert triggered
│
└─ No email sent


TIME: 11:00 AM
═════════════════════════════════════════════════════════════════════
User uploads receipt: Grocery - $200 (Budget: $500)
│
├─ Transaction saved to database (Total: $400, 80%)
├─ Dashboard loaded
├─ check_budget_alerts() called
│  │
│  ├─ Spending: $400 (80% of $500)
│  ├─ 80% >= threshold ✓
│  ├─ Create alert message
│  │
│  ├─ has_alert_been_sent_today('budget_warning', 'Food & Dining')?
│  │  └─ Query database
│  │     └─ Result: NO ✓ (not sent today)
│  │
│  ├─ ✅ ADD TO emails_to_send list
│  ├─ record_alert_sent('budget_warning', 'Food & Dining')
│  │  └─ INSERT into email_alert_history
│  │
│  └─ send_budget_alert_email()
│     └─ 📧 EMAIL SENT TO USER
│
└─ Console: "✅ Budget alert email sent for 1 category/categories"


TIME: 11:30 AM (same day)
═════════════════════════════════════════════════════════════════════
User uploads receipt: Coffee - $100 (Budget: $500)
│
├─ Transaction saved to database (Total: $500, 100%)
├─ Dashboard loaded
├─ check_budget_alerts() called
│  │
│  ├─ Spending: $500 (100% of $500)
│  ├─ 100% >= 100% threshold ✓
│  ├─ Create alert message
│  │
│  ├─ has_alert_been_sent_today('budget_danger', 'Food & Dining')?
│  │  └─ Query database
│  │     └─ Result: YES ✓ (sent at 11:00 AM!)
│  │
│  ├─ ❌ SKIP EMAIL (already sent)
│  │
│  └─ Alerts still displayed in dashboard
│
└─ Console: "📧 Budget alert already sent today for all triggered categories"


TIME: 11:45 AM (still same day)
═════════════════════════════════════════════════════════════════════
User uploads receipt: Dessert - $50 (Budget: $500)
│
├─ Transaction saved to database (Total: $550, 110%)
├─ Dashboard loaded
├─ check_budget_alerts() called
│  │
│  ├─ Spending: $550 (110% of $500)
│  ├─ 110% >= 100% threshold ✓
│  ├─ Create alert message
│  │
│  ├─ has_alert_been_sent_today('budget_danger', 'Food & Dining')?
│  │  └─ Query database
│  │     └─ Result: YES ✓ (sent at 11:00 AM!)
│  │
│  ├─ ❌ SKIP EMAIL (already sent)
│  │
│  └─ Alerts still displayed in dashboard
│
└─ Console: "📧 Budget alert already sent today for all triggered categories"


NEXT DAY: 12:01 AM
═════════════════════════════════════════════════════════════════════
User uploads receipt: Breakfast - $80 (Budget: $500)
│
├─ Transaction saved to database
├─ Dashboard loaded
├─ check_budget_alerts() called
│  │
│  ├─ Spending: $630 (126% of $500)
│  ├─ 126% >= 100% threshold ✓
│  ├─ Create alert message
│  │
│  ├─ has_alert_been_sent_today('budget_danger', 'Food & Dining')?
│  │  └─ Query database
│  │     └─ Result: NO ✓ (sent_date was '2025-11-01', today is '2025-11-02')
│  │
│  ├─ ✅ ADD TO emails_to_send list
│  ├─ record_alert_sent('budget_danger', 'Food & Dining')
│  │  └─ INSERT into email_alert_history (new date: 2025-11-02)
│  │
│  └─ send_budget_alert_email()
│     └─ 📧 EMAIL SENT TO USER (new day, new alert)
│
└─ Console: "✅ Budget alert email sent for 1 category/categories"
```

---

## Database Query Sequence

### Alert Checking Database Queries

```
QUERY 1: Get all budgets for user
┌──────────────────────────────────────────────┐
│ SELECT * FROM budgets                        │
│ WHERE user_id = ?                            │
└──────────────────────────────────────────────┘

QUERY 2: Calculate spending per category
┌──────────────────────────────────────────────┐
│ SELECT SUM(amount) as total                  │
│ FROM transactions                            │
│ WHERE user_id = ?                            │
│ AND category = ?                             │
│ AND type = 'expense'                         │
│ AND strftime('%Y-%m', date) = ?              │
└──────────────────────────────────────────────┘

QUERY 3: Check if alert sent today (NEW)
┌──────────────────────────────────────────────┐
│ SELECT id                                    │
│ FROM email_alert_history                    │
│ WHERE user_id = ?                            │
│ AND alert_type = ?                           │
│ AND category = ?                             │
│ AND sent_date = ?                            │
└──────────────────────────────────────────────┘

QUERY 4: Record alert sent (NEW)
┌──────────────────────────────────────────────┐
│ INSERT OR IGNORE INTO email_alert_history   │
│ (user_id, alert_type, category, sent_date)  │
│ VALUES (?, ?, ?, ?)                         │
└──────────────────────────────────────────────┘
```

---

## Data Flow for One Transaction

```
REQUEST: POST /add_transaction
│
├─ Parse form data
│  ├─ type: "expense"
│  ├─ amount: 200
│  ├─ category: "Food & Dining"
│  └─ date: "2025-11-01"
│
├─ INSERT INTO transactions
│  └─ new transaction saved
│
├─ REDIRECT to /dashboard
│
├─ GET /dashboard
│
├─ DATABASE QUERIES:
│  ├─ Get recent transactions
│  ├─ Get this month's summary
│  ├─ Get category breakdown
│  │
│  ├─ check_budget_alerts():
│  │  ├─ Query: Get all budgets
│  │  ├─ Query: Get total spent per category
│  │  ├─ Query: Check if alert sent today (NEW!)
│  │  └─ Query: Record alert sent (if needed) (NEW!)
│  │
│  └─ detect_anomalies():
│     ├─ Query: Get avg spending (30 days)
│     ├─ Query: Get unusual transactions (7 days)
│     ├─ Query: Check if alert sent today (NEW!)
│     └─ Query: Record alert sent (if needed) (NEW!)
│
├─ EMAIL SEND (if new alert):
│  └─ SMTP connection to send email
│
└─ RENDER dashboard.html with:
   ├─ Recent transactions
   ├─ Summary data
   ├─ Category breakdown
   ├─ Alerts (for display)
   └─ Anomalies (for display)
```

---

## Email Sending Decision Tree

```
Alert Detected (Budget >= 80% OR Anomaly Found)
│
├─ YES → Check if email sent today
│         │
│         ├─ YES (sent today)
│         │  └─ ❌ SKIP EMAIL
│         │      Alert still shown in dashboard
│         │      No email to inbox
│         │      Console: "📧 Alert already sent today"
│         │
│         └─ NO (not sent today)
│            ├─ ✅ SEND EMAIL
│            ├─ Record in email_alert_history
│            └─ Console: "✅ Email sent for X alert(s)"
│
└─ NO (no alert)
   └─ No email, no record
```

---

## Database Schema: email_alert_history

```
email_alert_history Table
┌────────────┬──────────────┬─────────────────────────────┐
│ Column     │ Type         │ Description                 │
├────────────┼──────────────┼─────────────────────────────┤
│ id         │ INTEGER PK   │ Primary key                 │
│ user_id    │ INTEGER FK   │ Reference to users table    │
│ alert_type │ TEXT         │ 'budget_warning',           │
│            │              │ 'budget_danger',            │
│            │              │ 'anomaly'                   │
│ category   │ TEXT         │ e.g., 'Food & Dining'       │
│ sent_date  │ TEXT         │ Format: 'YYYY-MM-DD'        │
│ created_at │ TIMESTAMP    │ When record was created     │
│ UNIQUE     │ Multiple     │ (user_id, alert_type,       │
│ Constraint │ Columns      │  category, sent_date)       │
└────────────┴──────────────┴─────────────────────────────┘
```

---

## Performance Comparison

### Before: Every check sends email if threshold met
```
10:00 → Alert check → Email sent ✉️
10:01 → Alert check → Email sent ✉️✉️
10:02 → Alert check → Email sent ✉️✉️✉️
10:03 → Alert check → Email sent ✉️✉️✉️✉️

Result: Exponential growth of emails
```

### After: Check prevents duplicates
```
10:00 → Alert check → has_sent_today? NO → Email sent ✉️
10:01 → Alert check → has_sent_today? YES → Skip
10:02 → Alert check → has_sent_today? YES → Skip
10:03 → Alert check → has_sent_today? YES → Skip

Result: Only 1 email sent
```

---

**This system ensures users are informed without being spammed!**

---

*Flow Diagram Version: 1.0*  
*Last Updated: 2025-11-01*  
*Status: Production Ready*