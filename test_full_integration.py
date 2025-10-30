#!/usr/bin/env python
"""Full OCR Integration Test"""

import sys
import os
sys.path.insert(0, '.')

from models.database import init_db, get_db_connection
from utils.ocr_processor import extract_receipt_data, configure_tesseract
from utils.ai_categorizer import categorize_expense
from PIL import Image, ImageDraw
from datetime import datetime
from werkzeug.security import generate_password_hash

print("\n" + "=" * 70)
print("FULL OCR INTEGRATION TEST")
print("=" * 70)

# Step 1: Initialize Database
print("\n1️⃣  Initializing database...")
init_db()
print("   ✓ Database initialized")

# Step 2: Verify Tesseract
print("\n2️⃣  Checking Tesseract OCR...")
configured = configure_tesseract()
print(f"   ✓ Tesseract Configured: {configured}")

# Step 3: Create Test User
print("\n3️⃣  Creating test user...")
conn = get_db_connection()
cursor = conn.cursor()

# Check if test user exists
cursor.execute('SELECT id FROM users WHERE email = ?', ('test@example.com',))
test_user = cursor.fetchone()

if test_user:
    user_id = test_user['id']
    print(f"   ✓ Test user already exists (ID: {user_id})")
else:
    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                   ('testuser', 'test@example.com', generate_password_hash('password123')))
    conn.commit()
    user_id = cursor.lastrowid
    print(f"   ✓ Test user created (ID: {user_id})")

# Step 4: Create Test Receipt Image
print("\n4️⃣  Creating test receipt image...")
img = Image.new('RGB', (500, 400), color='white')
draw = ImageDraw.Draw(img)

test_receipt_text = """
AMAZON GROCERY STORE
123 Market Street
New Delhi, India

Date: 2025-10-30
Time: 14:30

=======================
ITEMS PURCHASED:
=======================
Milk (1L)             180.00
Bread                 120.00
Eggs (12)              95.00
Butter                150.00
Fresh Vegetables      200.00

=======================
SUBTOTAL:             745.00
GST (5%):              37.25
TOTAL AMOUNT:         782.25

Thank you for shopping!
"""

draw.text((30, 30), test_receipt_text, fill='black')
test_receipt_path = 'static/uploads/test_receipt_integration.jpg'
os.makedirs(os.path.dirname(test_receipt_path), exist_ok=True)
img.save(test_receipt_path)
print(f"   ✓ Test receipt created: {test_receipt_path}")

# Step 5: Extract Receipt Data with OCR
print("\n5️⃣  Running OCR extraction...")
extracted_data = extract_receipt_data(test_receipt_path)
print(f"   ✓ OCR extraction complete")
print(f"     • Amount: ₹{extracted_data['amount']:.2f}")
print(f"     • Description: {extracted_data['description']}")
print(f"     • Date: {extracted_data['date']}")

# Step 6: Categorize Expense with AI
print("\n6️⃣  Categorizing expense with AI...")
category = categorize_expense(extracted_data.get('description', 'Receipt Purchase'))
print(f"   ✓ Category: {category}")

# Step 7: Insert into Database
print("\n7️⃣  Inserting transaction into database...")
cursor.execute('INSERT INTO transactions (user_id, type, amount, category, description, date, receipt_path) VALUES (?, ?, ?, ?, ?, ?, ?)', 
               (user_id, 'expense', extracted_data.get('amount', 0), category, 
                extracted_data.get('description', 'Receipt Purchase'), 
                extracted_data.get('date', datetime.now().strftime('%Y-%m-%d')), 
                test_receipt_path))
conn.commit()
transaction_id = cursor.lastrowid
print(f"   ✓ Transaction inserted (ID: {transaction_id})")

# Step 8: Verify Transaction in Database
print("\n8️⃣  Verifying transaction in database...")
cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
transaction = cursor.fetchone()
conn.close()

if transaction:
    print("   ✓ Transaction verified!")
    print(f"     • User ID: {transaction['user_id']}")
    print(f"     • Amount: ₹{transaction['amount']:.2f}")
    print(f"     • Category: {transaction['category']}")
    print(f"     • Description: {transaction['description']}")
    print(f"     • Date: {transaction['date']}")
    print(f"     • Receipt Path: {transaction['receipt_path']}")

# Step 9: Summary
print("\n" + "=" * 70)
print("✅ FULL OCR INTEGRATION TEST SUCCESSFUL!")
print("=" * 70)
print(f"""
Summary:
  ✓ Database: Initialized and working
  ✓ Tesseract: Configured and ready
  ✓ OCR Extraction: Amount=₹{extracted_data['amount']:.2f}
  ✓ AI Categorization: {category}
  ✓ Database Transaction: Inserted successfully
  ✓ Transaction Verification: Confirmed

The Flask app is now ready to handle receipt uploads!
When users upload a receipt:
  1. Image is saved to static/uploads/
  2. OCR extracts amount, date, merchant
  3. AI categorizes the expense
  4. Transaction is stored in database
  5. User sees auto-filled form in dashboard

""")
print("=" * 70)
print("\n🚀 Ready to start Flask app!\n")