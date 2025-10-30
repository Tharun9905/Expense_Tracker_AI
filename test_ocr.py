#!/usr/bin/env python
"""Test OCR functionality after Tesseract installation"""

import sys
sys.path.insert(0, '.')

from utils.ocr_processor import configure_tesseract, extract_receipt_data
from PIL import Image, ImageDraw
import os
from datetime import datetime

print("=" * 60)
print("OCR FUNCTIONALITY TEST")
print("=" * 60)

# Step 1: Check Tesseract Configuration
print("\n1. Checking Tesseract Configuration...")
configured = configure_tesseract()
print(f"   ✓ Tesseract Configured: {configured}")

# Step 2: Create a test receipt image
print("\n2. Creating test receipt image...")
img = Image.new('RGB', (500, 400), color='white')
draw = ImageDraw.Draw(img)

test_text = """
PREMIUM SUPERMARKET
Electronics Department
123 Market Street, City

Date: 2025-10-30
Time: 14:30

ITEMS:
Item 1              200.00
Item 2              150.00
Item 3              125.00

SUBTOTAL:           475.00
TAX (18%):           85.50
TOTAL AMOUNT:       560.50

Thank you for shopping!
"""

draw.text((30, 30), test_text, fill='black')
test_image_path = 'test_receipt.jpg'
img.save(test_image_path)
print(f"   ✓ Test receipt created: {test_image_path}")

# Step 3: Extract data using OCR
print("\n3. Running OCR extraction...")
result = extract_receipt_data(test_image_path)

# Step 4: Display results
print("\n" + "=" * 60)
print("OCR EXTRACTION RESULTS")
print("=" * 60)
print(f"Amount Extracted:    ₹{result['amount']:.2f}")
print(f"Description:         {result['description']}")
print(f"Date:                {result['date']}")
print(f"Raw Text Length:     {len(result.get('raw_text', ''))} characters")

# Verify the result is not zero
if result['amount'] > 0:
    print("\n✅ SUCCESS! OCR is working correctly!")
    print("   Receipt amount has been extracted (not ₹0.00)")
else:
    print("\n⚠️  WARNING: Amount extraction returned 0.00")
    print("   This might indicate OCR extraction issues")

# Cleanup
os.remove(test_image_path)
print("\n✓ Test file cleaned up")
print("=" * 60)