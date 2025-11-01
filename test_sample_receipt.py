#!/usr/bin/env python
"""Create sample test receipt for manual testing"""

from PIL import Image, ImageDraw
import os

# Create a realistic receipt image
img = Image.new('RGB', (600, 700), color='white')
draw = ImageDraw.Draw(img)

# Add a realistic receipt text
receipt_text = """
┌─────────────────────────────────────┐
│     RETAIL STORE INVOICE           │
│        Invoice #RET-2025-1234      │
└─────────────────────────────────────┘

Store: Metro Shopping Mall
Location: Delhi, India
Date: 30-Oct-2025
Time: 14:35

────────────────────────────────────

ITEMS PURCHASED:

Dairy Products          275.00
Fresh Fruits            320.00
Groceries              450.00
Household Items        280.00

────────────────────────────────────

Subtotal               1325.00
Tax (5%)                 66.25

TOTAL AMOUNT:          1391.25

────────────────────────────────────

Mode of Payment: Cash
Thank You!
"""

# Draw the text on the image
draw.text((40, 40), receipt_text, fill='black')

# Save the test receipt
test_path = 'static/uploads/sample_receipt_for_testing.jpg'
os.makedirs(os.path.dirname(test_path), exist_ok=True)
img.save(test_path)

print(f"✓ Sample receipt created: {test_path}")
print("\nYou can now:")
print("1. Open http://localhost:5000")
print("2. Login with: test@example.com / password123")
print("3. Go to 'Upload Receipt'")
print(f"4. Upload: {test_path}")
print("\nOCR will extract:")
print("  • Amount: ₹1391.25")
print("  • Merchant: RETAIL STORE / METRO SHOPPING")
print("  • Date: 2025-10-30")
print("  • Category: Auto-categorized")