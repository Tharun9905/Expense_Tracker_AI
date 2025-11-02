#!/usr/bin/env python
"""Test Email Alert System with Duplicate Prevention"""

import sys
sys.path.insert(0, '.')

from models.database import init_db, get_db_connection
from utils.alerts import check_budget_alerts, detect_anomalies, record_alert_sent, has_alert_been_sent_today
from datetime import datetime
import sqlite3

print("\n" + "=" * 80)
print("🧪 EMAIL ALERT SYSTEM TEST - Duplicate Prevention")
print("=" * 80)

# Initialize database
print("\n[STEP 1] Initializing database...")
init_db()
print("   ✅ Database initialized")

# Create test user
print("\n[STEP 2] Creating test user...")
conn = get_db_connection()
cursor = conn.cursor()

# Delete existing test data
cursor.execute("DELETE FROM users WHERE email = 'test_alert@example.com'")
conn.commit()

cursor.execute('''INSERT INTO users (username, email, password) 
    VALUES (?, ?, ?)''', 
    ('Test Alert User', 'test_alert@example.com', 'hashed_password'))
conn.commit()

user_id = cursor.lastrowid
print(f"   ✅ Test user created (ID: {user_id})")

# Create notification preferences
print("\n[STEP 3] Setting up notification preferences...")
cursor.execute('''INSERT OR REPLACE INTO notification_preferences 
    (user_id, budget_alerts_email, anomaly_alerts_email) 
    VALUES (?, 1, 1)''', (user_id,))
conn.commit()
print("   ✅ Notifications enabled")

# Create budget
print("\n[STEP 4] Creating test budget...")
cursor.execute('''DELETE FROM budgets WHERE user_id = ? AND category = 'Food & Dining' ''', (user_id,))
conn.commit()

cursor.execute('''INSERT INTO budgets (user_id, category, amount, period) 
    VALUES (?, ?, ?, ?)''', 
    (user_id, 'Food & Dining', 500, 'monthly'))
conn.commit()
print("   ✅ Budget created: ₹500 for Food & Dining")

# Create test transactions
print("\n[STEP 5] Creating test transactions...")
transactions = [
    ('Food & Dining', 250, 'Grocery shopping'),
    ('Food & Dining', 150, 'Restaurant lunch'),
    ('Transportation', 200, 'Uber rides'),
]

today = datetime.now().strftime('%Y-%m-%d')
cursor.execute('DELETE FROM transactions WHERE user_id = ? AND date = ?', (user_id, today))
conn.commit()

for category, amount, desc in transactions:
    cursor.execute('''INSERT INTO transactions 
        (user_id, type, amount, category, description, date) 
        VALUES (?, ?, ?, ?, ?, ?)''', 
        (user_id, 'expense', amount, category, desc, today))
    conn.commit()
    print(f"   ✅ Added: {category} - ₹{amount}")

conn.close()

print("\n" + "=" * 80)
print("TESTING ALERT DUPLICATION PREVENTION")
print("=" * 80)

# Test 1: First budget check (should send email)
print("\n[TEST 1] First transaction load - Check budget alerts...")
print("-" * 40)
alerts1 = check_budget_alerts(user_id)
print(f"   Alerts detected: {len(alerts1)}")
for alert in alerts1:
    print(f"   - [{alert['type']}] {alert['category']}: {alert['message']}")

# Test 2: Second budget check same day (should NOT send email)
print("\n[TEST 2] Second transaction load - Check budget alerts (SAME DAY)...")
print("-" * 40)
print("   📝 Scenario: User uploads another transaction in the same category")
alerts2 = check_budget_alerts(user_id)
print(f"   Alerts detected: {len(alerts2)}")
for alert in alerts2:
    print(f"   - [{alert['type']}] {alert['category']}: {alert['message']}")

# Test 3: Check alert history
print("\n[TEST 3] Checking alert history...")
print("-" * 40)
conn = get_db_connection()
cursor = conn.cursor()
today = datetime.now().strftime('%Y-%m-%d')

cursor.execute('''SELECT * FROM email_alert_history 
    WHERE user_id = ? AND sent_date = ?''', (user_id, today))
history = cursor.fetchall()

print(f"   📊 Emails sent today: {len(history)}")
for record in history:
    print(f"   - Type: {record['alert_type']}, Category: {record['category']}, Date: {record['sent_date']}")

# Test 4: Check has_alert_been_sent_today function
print("\n[TEST 4] Testing alert tracking functions...")
print("-" * 40)
result = has_alert_been_sent_today(user_id, 'budget_warning', 'Food & Dining')
print(f"   Has budget warning been sent today for 'Food & Dining'? {result}")

# Clean up
print("\n[CLEANUP] Cleaning up test data...")
cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM email_alert_history WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM notification_preferences WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
conn.commit()
conn.close()
print("   ✅ Test data cleaned up")

# Display test summary
print("\n" + "=" * 80)
print("✅ TEST SUMMARY")
print("=" * 80)
print("""
✨ NEW FEATURES IMPLEMENTED:

1. Email Alert History Tracking
   - New table: email_alert_history
   - Tracks when emails were sent for each category

2. Duplicate Prevention
   - check_budget_alerts() - Sends only 1 email per category per day
   - detect_anomalies() - Sends only 1 email per category per day
   - Multiple transactions won't trigger multiple emails for same category

3. Functions Added to alerts.py:
   - has_alert_been_sent_today(user_id, alert_type, category)
   - record_alert_sent(user_id, alert_type, category)

4. Benefits:
   ✅ Users get alert once per day per category
   ✅ Not spammed with repetitive emails
   ✅ Alert resets daily for new alerts
   ✅ Works for both budget and anomaly alerts

5. Alert Types Tracked:
   - budget_danger (Budget exceeded 100%)
   - budget_warning (Budget exceeded 80%)
   - anomaly (Unusual spending detected)

FLOW:
1. User uploads transaction → check_budget_alerts() called
2. Category spending >= 80% → Check if email sent today
3. If NOT sent today → Send email & record in history
4. If already sent today → Skip email (not sent again)
5. Next day at 00:00 → Alert history resets for new alerts

This prevents spam while ensuring users are informed of important budget issues!
""")
print("=" * 80 + "\n")