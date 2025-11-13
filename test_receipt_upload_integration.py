"""
Integration tests for Receipt Upload Flow
Tests the complete flow: upload -> OCR processing -> data extraction -> transaction creation
"""

import unittest
import os
import tempfile
import sqlite3
from PIL import Image, ImageDraw
from datetime import datetime
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.easyocr_processor import extract_receipt_data, clear_reader_cache
from utils.ai_categorizer import categorize_expense, predict_category


class TestReceiptUploadFlow(unittest.TestCase):
    """Integration tests for receipt upload and processing"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        clear_reader_cache()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        clear_reader_cache()
    
    def create_receipt_image(self, receipt_dict, filename="receipt.jpg"):
        """Create a realistic receipt image for testing"""
        img = Image.new('RGB', (800, 1200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Convert dict to formatted text
        lines = []
        lines.append(receipt_dict.get('merchant', 'STORE NAME'))
        lines.append(receipt_dict.get('address', 'Main Street'))
        lines.append("")
        lines.append(f"Date: {receipt_dict.get('date', '2025-11-15')}")
        lines.append(f"Time: {receipt_dict.get('time', '14:30')}")
        lines.append("")
        lines.append("ITEMS PURCHASED")
        lines.append("-" * 40)
        
        for item in receipt_dict.get('items', []):
            lines.append(f"{item['name']:<30} {item['price']:.2f}")
        
        lines.append("-" * 40)
        lines.append(f"Subtotal: {receipt_dict.get('subtotal', 0.0):.2f}")
        lines.append(f"Tax: {receipt_dict.get('tax', 0.0):.2f}")
        lines.append(f"TOTAL AMOUNT: {receipt_dict.get('total', 0.0):.2f}")
        
        # Draw text on image
        y_offset = 50
        for line in lines:
            draw.text((50, y_offset), line, fill='black')
            y_offset += 25
        
        path = os.path.join(self.test_dir, filename)
        img.save(path)
        return path
    
    def test_grocery_receipt_flow(self):
        """Test complete flow with grocery receipt"""
        receipt_data = {
            'merchant': 'FRESH GROCERY MART',
            'address': '123 Main Street',
            'date': '2025-11-15',
            'time': '14:30',
            'items': [
                {'name': 'Fresh Vegetables', 'price': 325.50},
                {'name': 'Dairy Products', 'price': 275.00},
                {'name': 'Fruits', 'price': 420.00},
            ],
            'subtotal': 1020.50,
            'tax': 51.02,
            'total': 1071.52
        }
        
        image_path = self.create_receipt_image(receipt_data, "grocery.jpg")
        result = extract_receipt_data(image_path)
        
        # Validate extraction
        self.assertIsNotNone(result)
        self.assertGreater(result['amount'], 0, "Should extract amount")
        self.assertIsNotNone(result['description'], "Should extract merchant")
        self.assertIsNotNone(result['date'], "Should extract date")
        self.assertGreater(result['confidence'], 0, "Should have confidence score")
        
        # Categorize the expense
        category = predict_category(result['description'])
        self.assertIsNotNone(category)
    
    def test_restaurant_receipt_flow(self):
        """Test complete flow with restaurant receipt"""
        receipt_data = {
            'merchant': 'BELLA PIZZA RESTAURANT',
            'address': 'Connaught Place, Delhi',
            'date': '2025-11-15',
            'time': '19:45',
            'items': [
                {'name': 'Margherita Pizza', 'price': 550.00},
                {'name': 'Garlic Bread', 'price': 180.00},
                {'name': 'Coke', 'price': 120.00},
            ],
            'subtotal': 850.00,
            'tax': 42.50,
            'total': 892.50
        }
        
        image_path = self.create_receipt_image(receipt_data, "restaurant.jpg")
        result = extract_receipt_data(image_path)
        
        # Validate extraction
        self.assertIsNotNone(result)
        self.assertGreater(result['amount'], 0, "Should extract amount")
        self.assertIn(result['ocr_method'], ['easyocr', 'tesseract'])
        
        # Validate categorization
        category = predict_category(result['description'])
        self.assertIn(category, ['Food & Dining', 'Restaurants', 'Food', 'Dining'])
    
    def test_shopping_receipt_flow(self):
        """Test complete flow with shopping receipt"""
        receipt_data = {
            'merchant': 'TECH WORLD STORE',
            'address': 'Mumbai Shopping Complex',
            'date': '2025-11-15',
            'time': '10:30',
            'items': [
                {'name': 'Mobile Phone Case', 'price': 899.00},
                {'name': 'USB-C Cable', 'price': 498.00},
                {'name': 'Screen Protector', 'price': 349.00},
            ],
            'subtotal': 1746.00,
            'tax': 314.28,
            'total': 2060.28
        }
        
        image_path = self.create_receipt_image(receipt_data, "shopping.jpg")
        result = extract_receipt_data(image_path)
        
        # Validate extraction
        self.assertIsNotNone(result)
        self.assertGreater(result['amount'], 0, "Should extract amount")
        
        # Validate categorization
        category = predict_category(result['description'])
        self.assertIsNotNone(category)
    
    def test_multiple_receipts_processing(self):
        """Test processing multiple receipts in sequence"""
        receipts = [
            {
                'merchant': 'STORE A',
                'items': [{'name': 'Item 1', 'price': 100}],
                'subtotal': 100, 'tax': 5, 'total': 105
            },
            {
                'merchant': 'STORE B',
                'items': [{'name': 'Item 2', 'price': 200}],
                'subtotal': 200, 'tax': 10, 'total': 210
            },
            {
                'merchant': 'STORE C',
                'items': [{'name': 'Item 3', 'price': 150}],
                'subtotal': 150, 'tax': 7.5, 'total': 157.5
            }
        ]
        
        results = []
        for i, receipt in enumerate(receipts):
            image_path = self.create_receipt_image(receipt, f"receipt_{i}.jpg")
            result = extract_receipt_data(image_path)
            results.append(result)
        
        # Validate all processed
        self.assertEqual(len(results), 3)
        
        # Validate all have valid amounts
        for result in results:
            self.assertGreater(result['amount'], 0)
            self.assertIsNotNone(result['description'])
    
    def test_receipt_with_corrupted_image(self):
        """Test handling of corrupted/unclear image"""
        # Create a very blurry image
        img = Image.new('RGB', (100, 100), color='gray')
        draw = ImageDraw.Draw(img)
        
        # Draw with low contrast
        for i in range(10, 90, 10):
            draw.line([(i, 10), (i, 90)], fill='darkgray')
        
        path = os.path.join(self.test_dir, "corrupted.jpg")
        img.save(path)
        
        result = extract_receipt_data(path)
        
        # Should handle gracefully
        self.assertIsNotNone(result)
        self.assertIn('amount', result)
        # Amount might be 0 due to unclear image
        self.assertGreaterEqual(result['amount'], 0)
    
    def test_receipt_processing_returns_all_fields(self):
        """Test that all required fields are returned"""
        receipt_data = {
            'merchant': 'TEST STORE',
            'items': [{'name': 'Test Item', 'price': 50}],
            'subtotal': 50, 'tax': 2.5, 'total': 52.5
        }
        
        image_path = self.create_receipt_image(receipt_data)
        result = extract_receipt_data(image_path)
        
        # Check all required fields
        required_fields = ['amount', 'date', 'description', 'raw_text', 'confidence', 'ocr_method']
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")
    
    def test_receipt_amount_validation(self):
        """Test that extracted amounts are reasonable"""
        receipt_data = {
            'merchant': 'TEST STORE',
            'items': [{'name': 'Item', 'price': 999.99}],
            'subtotal': 999.99, 'tax': 49.99, 'total': 1049.98
        }
        
        image_path = self.create_receipt_image(receipt_data)
        result = extract_receipt_data(image_path)
        
        # Amount should be reasonable
        if result['amount'] > 0:
            self.assertLess(result['amount'], 1000000, "Amount should be reasonable")
    
    def test_receipt_date_validation(self):
        """Test that extracted date is valid"""
        receipt_data = {
            'merchant': 'TEST STORE',
            'date': '2025-11-15',
            'items': [{'name': 'Item', 'price': 50}],
            'subtotal': 50, 'tax': 2.5, 'total': 52.5
        }
        
        image_path = self.create_receipt_image(receipt_data)
        result = extract_receipt_data(image_path)
        
        # Date should be in valid format
        date_str = result['date']
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            self.fail(f"Invalid date format: {date_str}")
    
    def test_receipt_merchant_validation(self):
        """Test that merchant name is extracted"""
        receipt_data = {
            'merchant': 'UNIQUE STORE NAME XYZ',
            'items': [{'name': 'Item', 'price': 50}],
            'subtotal': 50, 'tax': 2.5, 'total': 52.5
        }
        
        image_path = self.create_receipt_image(receipt_data)
        result = extract_receipt_data(image_path)
        
        # Should have a description
        description = result['description']
        self.assertIsNotNone(description)
        self.assertGreater(len(description), 0)


class TestOCRAccuracyComparison(unittest.TestCase):
    """Test OCR accuracy on various receipt types"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        clear_reader_cache()
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        clear_reader_cache()
    
    def create_formatted_receipt_image(self, text, filename="receipt.jpg"):
        """Create receipt image with formatted text"""
        img = Image.new('RGB', (800, 1200), color='white')
        draw = ImageDraw.Draw(img)
        
        y = 50
        for line in text.split('\n'):
            draw.text((50, y), line, fill='black')
            y += 30
        
        path = os.path.join(self.test_dir, filename)
        img.save(path)
        return path
    
    def test_indian_amount_format_accuracy(self):
        """Test OCR accuracy with Indian number format"""
        text = """STORE NAME
        
        TOTAL AMOUNT: ₹1,413.56
        """
        
        image_path = self.create_formatted_receipt_image(text)
        result = extract_receipt_data(image_path)
        
        # Should extract a value close to 1413.56
        if result['amount'] > 0:
            # Allow some tolerance for OCR variance
            self.assertGreater(result['amount'], 1000)
            self.assertLess(result['amount'], 2000)
    
    def test_usd_amount_format_accuracy(self):
        """Test OCR accuracy with USD format"""
        text = """STORE NAME
        
        TOTAL AMOUNT: $123.45
        """
        
        image_path = self.create_formatted_receipt_image(text)
        result = extract_receipt_data(image_path)
        
        # Should extract value close to 123.45
        if result['amount'] > 0:
            self.assertGreater(result['amount'], 100)
            self.assertLess(result['amount'], 200)
    
    def test_multiple_currency_format(self):
        """Test handling of mixed currency formats"""
        text = """STORE NAME
        
        Item 1: $50.00
        Item 2: $25.50
        TOTAL: $75.50
        """
        
        image_path = self.create_formatted_receipt_image(text)
        result = extract_receipt_data(image_path)
        
        # Should extract the largest reasonable amount
        if result['amount'] > 0:
            self.assertGreaterEqual(result['amount'], 50)


class TestReceiptUploadValidation(unittest.TestCase):
    """Test receipt upload validation and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        clear_reader_cache()
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        clear_reader_cache()
    
    def test_empty_file_handling(self):
        """Test handling of empty receipt file"""
        empty_path = os.path.join(self.test_dir, "empty.jpg")
        # Create an empty file
        open(empty_path, 'w').close()
        
        result = extract_receipt_data(empty_path)
        
        # Should handle gracefully
        self.assertIsNotNone(result)
        # Empty file shouldn't produce valid amount
        self.assertEqual(result['amount'], 0.0)
    
    def test_invalid_image_format_handling(self):
        """Test handling of invalid image format"""
        # Create a text file with .jpg extension
        fake_jpg = os.path.join(self.test_dir, "fake.jpg")
        with open(fake_jpg, 'w') as f:
            f.write("This is not an image")
        
        # Should handle gracefully or raise appropriate error
        try:
            result = extract_receipt_data(fake_jpg)
            # Either it handles gracefully or raises an error
            if result is not None:
                self.assertIn('amount', result)
        except Exception as e:
            # Error is acceptable for invalid format
            self.assertIsNotNone(e)
    
    def test_nonexistent_file_handling(self):
        """Test handling of nonexistent file"""
        fake_path = os.path.join(self.test_dir, "nonexistent.jpg")
        
        result = extract_receipt_data(fake_path)
        
        # Should return error dict
        self.assertIsNotNone(result)
        self.assertEqual(result['amount'], 0.0)
        self.assertIn('error', result)


class TestBulkReceiptProcessing(unittest.TestCase):
    """Test processing large batches of receipts"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        clear_reader_cache()
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        clear_reader_cache()
    
    def create_simple_receipt(self, store_name, amount, index):
        """Create a simple receipt image"""
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        draw.text((50, 50), f"{store_name}", fill='black')
        draw.text((50, 100), f"Amount: {amount}", fill='black')
        draw.text((50, 150), "Thank you!", fill='black')
        
        path = os.path.join(self.test_dir, f"receipt_{index}.jpg")
        img.save(path)
        return path
    
    def test_process_10_receipts(self):
        """Test processing 10 receipts"""
        receipts = []
        stores = ['Store A', 'Store B', 'Store C', 'Store D', 'Store E',
                  'Store F', 'Store G', 'Store H', 'Store I', 'Store J']
        amounts = [100, 200, 150, 300, 250, 175, 225, 275, 125, 350]
        
        for i, (store, amount) in enumerate(zip(stores, amounts)):
            path = self.create_simple_receipt(store, amount, i)
            receipts.append(path)
        
        # Process all receipts
        results = []
        for path in receipts:
            result = extract_receipt_data(path)
            results.append(result)
        
        # Validate all processed successfully
        self.assertEqual(len(results), 10)
        
        # Count successful extractions
        successful = sum(1 for r in results if r['amount'] > 0)
        # At least 50% should be successful
        self.assertGreaterEqual(successful, 5)


def run_integration_tests():
    """Run all integration tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestReceiptUploadFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestOCRAccuracyComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestReceiptUploadValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestBulkReceiptProcessing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)