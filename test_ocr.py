#!/usr/bin/env python
"""Comprehensive OCR + AI Categorization Test"""

import sys
sys.path.insert(0, '.')

from utils.ocr_processor import configure_tesseract, extract_receipt_data
from utils.ai_categorizer import categorize_expense, predict_category
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

print("\n" + "=" * 80)
print("🧪 COMPREHENSIVE OCR + AI CATEGORIZATION TEST")
print("=" * 80)

# Step 1: Check Tesseract Configuration
print("\n[STEP 1/5] Checking Tesseract Configuration...")
configured = configure_tesseract()
if configured:
    print("   ✅ Tesseract OCR is properly configured")
else:
    print("   ⚠️  Tesseract OCR not configured - some features will be limited")

# Step 2: Create realistic test receipts
print("\n[STEP 2/5] Creating realistic test receipt images...")

test_receipts = [
    {
        'name': 'grocery_store',
        'text': """
FRESH GROCERY MART
123 Main Street, New Delhi
Phone: 011-XXXX-XXXX

Date: 30-Oct-2025
Time: 14:30 PM
Cashier: Rajesh

──────────────────────────
ITEMS PURCHASED
──────────────────────────

Fresh Vegetables        325.50
Dairy Products          275.00
Fruits (Organic)        420.00
Bread & Bakery          180.00
Spices Package          145.75

──────────────────────────
Subtotal              1346.25
GST (5%)                 67.31
TOTAL AMOUNT:         1413.56
──────────────────────────

Mode: CASH
Thank you for shopping!
Visit again soon!
""",
        'expected_amount': 1413.56,
        'expected_category': 'Food & Dining'
    },
    {
        'name': 'restaurant',
        'text': """
BELLA PIZZA RESTAURANT
Connaught Place, Delhi
PH: +91-11-XXXX-XXXX

Date: 01-Nov-2025
Time: 19:45
Bill #: 4521

────────────────────
MENU ITEMS
────────────────────

Margherita Pizza L      550.00
Garlic Bread (4pcs)     180.00
Coke 300ml (2)          120.00
Tiramisu                250.00

────────────────────
SUBTOTAL           1100.00
Service Charge 10%  110.00
GST 5%               60.50
────────────────────
TOTAL PAYABLE:    1270.50
────────────────────

Payment: Card
Thank You!
""",
        'expected_amount': 1270.50,
        'expected_category': 'Food & Dining'
    },
    {
        'name': 'electronics',
        'text': """
TECH WORLD STORE
Electronics & Gadgets
Mumbai Shopping Complex

Date: 02-Nov-2025
Invoice: TW-20251102-789

───────────────────────
PRODUCT DETAILS
───────────────────────

Mobile Phone Case      899.00
USB-C Cable (2x)       498.00
Screen Protector      349.00

───────────────────────
Subtotal:           1746.00
Tax (18%):            314.28
───────────────────────
TOTAL AMOUNT:      2060.28
───────────────────────

Thank You!
""",
        'expected_amount': 2060.28,
        'expected_category': 'Shopping'
    },
    {
        'name': 'pharmacy',
        'text': """
HEALTH PLUS PHARMACY
Medical & Wellness Store
Bangalore, Karnataka

Date: 03-Nov-2025
Rx #: HP-2025-1156

─────────────────────
MEDICINES & SUPPLIES
─────────────────────

Aspirin Tablets        145.00
Vitamin C Tablets      320.00
First Aid Kit         850.00
Thermometer           299.00

─────────────────────
Subtotal:           1614.00
Tax:                  96.84
─────────────────────
TOTAL:             1710.84
─────────────────────

Visit us again!
""",
        'expected_amount': 1710.84,
        'expected_category': 'Healthcare'
    }
]

# Create test images
test_images = []
for receipt in test_receipts:
    img = Image.new('RGB', (800, 900), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), receipt['text'], fill='black')
    
    image_path = f"test_receipt_{receipt['name']}.jpg"
    img.save(image_path)
    test_images.append({
        'path': image_path,
        'name': receipt['name'],
        'expected_amount': receipt['expected_amount'],
        'expected_category': receipt['expected_category']
    })
    print(f"   ✅ Created: {image_path}")

# Step 3: Extract data using OCR
print("\n[STEP 3/5] Running OCR extraction on all receipts...")
print("-" * 80)

ocr_results = []
for test_img in test_images:
    print(f"\n📄 Processing: {test_img['name'].upper()}")
    result = extract_receipt_data(test_img['path'])
    result['image_name'] = test_img['name']
    result['expected_amount'] = test_img['expected_amount']
    result['expected_category'] = test_img['expected_category']
    ocr_results.append(result)
    
    print(f"   Amount: ₹{result['amount']:.2f}")
    print(f"   Merchant: {result['description']}")
    print(f"   Date: {result['date']}")

# Step 4: AI Categorization
print("\n[STEP 4/5] Running AI Categorization...")
print("-" * 80)

categorization_results = []
for result in ocr_results:
    print(f"\n🤖 Categorizing: {result['image_name'].upper()}")
    
    # Method 1: Simple categorization
    simple_category = categorize_expense(result['description'])
    
    # Method 2: Predict category with scoring
    predicted_category = predict_category(result['description'])
    
    print(f"   Description: {result['description']}")
    print(f"   Simple Category: {simple_category}")
    print(f"   Predicted Category: {predicted_category}")
    print(f"   Expected Category: {result['expected_category']}")
    
    categorization_results.append({
        'image_name': result['image_name'],
        'description': result['description'],
        'simple_category': simple_category,
        'predicted_category': predicted_category,
        'expected_category': result['expected_category'],
        'amount': result['amount']
    })

# Step 5: Validation & Results
print("\n[STEP 5/5] Validation & Results")
print("=" * 80)

all_passed = True
summary = {
    'total_tests': len(test_images),
    'ocr_passed': 0,
    'category_passed': 0,
    'details': []
}

for i, result in enumerate(ocr_results, 1):
    category_result = categorization_results[i-1]
    
    print(f"\n📊 TEST {i}: {result['image_name'].upper()}")
    print("-" * 40)
    
    # OCR Validation
    ocr_passed = result['amount'] > 0
    if ocr_passed:
        print(f"   ✅ OCR: Amount extracted ₹{result['amount']:.2f}")
        summary['ocr_passed'] += 1
    else:
        print(f"   ❌ OCR: Failed to extract amount")
        all_passed = False
    
    # Category Validation
    category_match = category_result['predicted_category'] == result['expected_category']
    if category_match:
        print(f"   ✅ AI: Correctly categorized as '{category_result['predicted_category']}'")
        summary['category_passed'] += 1
    else:
        print(f"   ⚠️  AI: Predicted '{category_result['predicted_category']}' (expected '{result['expected_category']}')")
    
    # Data extraction details
    print(f"   📝 Merchant: {result['description']}")
    print(f"   📅 Date: {result['date']}")
    print(f"   💰 Amount: ₹{result['amount']:.2f}")
    
    summary['details'].append({
        'name': result['image_name'],
        'ocr_ok': ocr_passed,
        'category_ok': category_match
    })

# Final Summary
print("\n" + "=" * 80)
print("📈 TEST SUMMARY")
print("=" * 80)
print(f"Total Tests Run:       {summary['total_tests']}")
print(f"OCR Tests Passed:      {summary['ocr_passed']}/{summary['total_tests']} ✅" if summary['ocr_passed'] == summary['total_tests'] else f"OCR Tests Passed:      {summary['ocr_passed']}/{summary['total_tests']} ⚠️")
print(f"AI Category Passed:    {summary['category_passed']}/{summary['total_tests']} ✅" if summary['category_passed'] == summary['total_tests'] else f"AI Category Passed:    {summary['category_passed']}/{summary['total_tests']} ⚠️")

if all_passed and summary['category_passed'] == summary['total_tests']:
    print("\n🎉 ALL TESTS PASSED! OCR + AI Pipeline is working correctly!")
elif summary['ocr_passed'] == summary['total_tests']:
    print("\n✅ OCR is working! AI categorization needs fine-tuning.")
else:
    print("\n❌ Some tests failed. Check Tesseract installation and configuration.")

# Cleanup
print("\n[CLEANUP] Removing test files...")
for test_img in test_images:
    try:
        os.remove(test_img['path'])
        print(f"   ✓ Removed: {test_img['path']}")
    except:
        pass

print("\n" + "=" * 80)
print("✨ TEST COMPLETE")
print("=" * 80 + "\n")