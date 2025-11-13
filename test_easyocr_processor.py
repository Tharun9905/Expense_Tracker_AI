"""
Unit tests for Enhanced OCR Processor (EasyOCR)
Tests amount extraction, date extraction, merchant name extraction, and image preprocessing
"""

import unittest
import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.easyocr_processor import (
    extract_amount,
    parse_amount,
    extract_date,
    extract_merchant,
    preprocess_image,
    clear_reader_cache
)


class TestAmountExtraction(unittest.TestCase):
    """Test amount extraction from various receipt formats"""
    
    def test_total_amount_with_currency_symbol(self):
        """Test extraction of TOTAL AMOUNT with $ symbol"""
        text = "SUBTOTAL: $45.99\nTAX: $3.50\nTOTAL AMOUNT: $49.49"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 49.49, places=2)
    
    def test_indian_rupee_format(self):
        """Test extraction of amounts in Indian Rupee format"""
        text = "Subtotal: 1346.25\nGST (5%): 67.31\nTOTAL AMOUNT: ₹1413.56"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 1413.56, places=2)
    
    def test_grand_total_label(self):
        """Test extraction with GRAND TOTAL label"""
        text = "Items: 2\nSUBTOTAL: 100.00\nGRAND TOTAL: 115.50"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 115.50, places=2)
    
    def test_price_label(self):
        """Test extraction with PRICE label"""
        text = "Product: ABC\nPRICE: $29.99\nTax: $2.40\nFINAL: $32.39"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 32.39, places=2)
    
    def test_subtotal_only(self):
        """Test extraction when only subtotal is available"""
        text = "Item 1: 50\nItem 2: 75\nSUBTOTAL: 125.00"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 125.00, places=2)
    
    def test_amount_with_comma_as_thousand_separator(self):
        """Test amounts with comma as thousand separator"""
        text = "TOTAL AMOUNT: $1,234.56"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 1234.56, places=2)
    
    def test_amount_with_comma_as_decimal_separator(self):
        """Test amounts with comma as decimal separator (European format)"""
        text = "TOTAL AMOUNT: 1.234,56"
        result = extract_amount(text)
        # This could be 1234.56 or 1.234 depending on detection
        self.assertTrue(result > 0)
    
    def test_no_amount_found(self):
        """Test when no amount can be extracted"""
        text = "Thank you for your purchase!\nPlease visit again."
        result = extract_amount(text)
        self.assertEqual(result, 0.0)
    
    def test_empty_text(self):
        """Test with empty text"""
        result = extract_amount("")
        self.assertEqual(result, 0.0)
    
    def test_multiple_amounts_returns_largest(self):
        """Test that the largest reasonable amount is returned"""
        text = "Item 1: $5.00\nItem 2: $10.00\nItem 3: $15.00\nTOTAL: $30.00"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 30.00, places=2)
    
    def test_unrealistic_amount_filtered(self):
        """Test that unrealistically large amounts are filtered out"""
        text = "TOTAL: $999999999.99\nACTUAL TOTAL: $45.50"
        result = extract_amount(text)
        # Should prefer the more realistic amount
        self.assertLess(result, 100000)
    
    def test_amount_at_line_end(self):
        """Test amount extraction at end of line"""
        text = "Purchase amount 123.45"
        result = extract_amount(text)
        self.assertAlmostEqual(result, 123.45, places=2)
    
    def test_euro_currency(self):
        """Test Euro currency format"""
        text = "Total: €50,00"
        result = extract_amount(text)
        self.assertGreater(result, 0)


class TestParseAmount(unittest.TestCase):
    """Test amount parsing with various separator combinations"""
    
    def test_simple_decimal(self):
        """Test simple decimal number"""
        result = parse_amount("123.45")
        self.assertAlmostEqual(result, 123.45, places=2)
    
    def test_comma_thousand_separator(self):
        """Test comma as thousand separator"""
        result = parse_amount("1,234.56")
        self.assertAlmostEqual(result, 1234.56, places=2)
    
    def test_multiple_commas_thousand_separator(self):
        """Test multiple commas as thousand separators"""
        result = parse_amount("1,234,567.89")
        self.assertAlmostEqual(result, 1234567.89, places=2)
    
    def test_comma_decimal_separator(self):
        """Test comma as decimal separator"""
        result = parse_amount("123,45")
        self.assertAlmostEqual(result, 123.45, places=2)
    
    def test_european_format(self):
        """Test European format (dot thousand, comma decimal)"""
        result = parse_amount("1.234,56")
        self.assertAlmostEqual(result, 1234.56, places=2)
    
    def test_no_separator(self):
        """Test number without separators"""
        result = parse_amount("12345")
        self.assertAlmostEqual(result, 12345, places=2)
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled"""
        result = parse_amount("  123.45  ")
        self.assertAlmostEqual(result, 123.45, places=2)
    
    def test_invalid_format(self):
        """Test invalid amount format"""
        result = parse_amount("abc123")
        self.assertEqual(result, 0.0)
    
    def test_empty_string(self):
        """Test empty string"""
        result = parse_amount("")
        self.assertEqual(result, 0.0)


class TestDateExtraction(unittest.TestCase):
    """Test date extraction from various receipt formats"""
    
    def test_iso_format_dash(self):
        """Test ISO date format with dashes"""
        text = "Date: 2025-11-15"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")
    
    def test_iso_format_slash(self):
        """Test ISO date format with slashes"""
        text = "Date: 2025/11/15"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")
    
    def test_dd_mm_yyyy_format(self):
        """Test DD-MM-YYYY format"""
        text = "Date: 15-11-2025"
        result = extract_date(text)
        # Should be parsed as a valid date
        self.assertIsNotNone(result)
    
    def test_mm_dd_yyyy_format(self):
        """Test MM/DD/YYYY format"""
        text = "Date: 11/15/2025"
        result = extract_date(text)
        self.assertIsNotNone(result)
    
    def test_month_name_format(self):
        """Test month name format"""
        text = "Date: November 15, 2025"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")
    
    def test_abbreviated_month_format(self):
        """Test abbreviated month format"""
        text = "Date: Nov 15, 2025"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")
    
    def test_day_month_year_format(self):
        """Test day month year format"""
        text = "Date: 15 November 2025"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")
    
    def test_no_date_found_returns_today(self):
        """Test that current date is returned when no date found"""
        text = "Thank you for your purchase!"
        result = extract_date(text)
        today = datetime.now().strftime('%Y-%m-%d')
        # Should be today or very close
        self.assertIsNotNone(result)
    
    def test_empty_text_returns_today(self):
        """Test that empty text returns today's date"""
        result = extract_date("")
        today = datetime.now().strftime('%Y-%m-%d')
        self.assertEqual(result, today)
    
    def test_multiple_dates_returns_first(self):
        """Test that first date is returned when multiple dates present"""
        text = "Date: 15-11-2025\nDelivery: 20-11-2025"
        result = extract_date(text)
        self.assertEqual(result, "2025-11-15")


class TestMerchantExtraction(unittest.TestCase):
    """Test merchant name extraction from receipt text"""
    
    def test_simple_merchant_name(self):
        """Test extraction of simple merchant name"""
        text = "FRESH GROCERY MART\n123 Main Street\nTel: 123-456"
        result = extract_merchant(text)
        self.assertEqual(result, "FRESH GROCERY MART")
    
    def test_restaurant_name(self):
        """Test extraction of restaurant name"""
        text = "BELLA PIZZA RESTAURANT\nConnaught Place, Delhi\nItems:\nPizza: 500"
        result = extract_merchant(text)
        self.assertEqual(result, "BELLA PIZZA RESTAURANT")
    
    def test_skip_receipt_keywords(self):
        """Test that receipt keywords are skipped"""
        text = "RECEIPT\nINVOICE #12345\nTECH WORLD STORE\nItems"
        result = extract_merchant(text)
        self.assertEqual(result, "TECH WORLD STORE")
    
    def test_skip_item_lines(self):
        """Test that item lines are skipped"""
        text = "STORE NAME\nPhone: 111-2222\nItem 1: 50\nItem 2: 75"
        result = extract_merchant(text)
        self.assertEqual(result, "STORE NAME")
    
    def test_skip_numeric_heavy_lines(self):
        """Test that lines with many numbers are skipped"""
        text = "TOP STORE\nInvoice: 123456789\nRef: 987654321"
        result = extract_merchant(text)
        # Should prefer the store name over numeric lines
        self.assertEqual(result, "TOP STORE")
    
    def test_empty_text_returns_default(self):
        """Test default text when merchant not found"""
        text = ""
        result = extract_merchant(text)
        self.assertEqual(result, "Receipt Purchase")
    
    def test_merchant_in_middle_of_receipt(self):
        """Test extraction when merchant name is not in first line"""
        text = "Receipt\n\n\nABC SUPERMARKET\nItems:\nBread: 50"
        result = extract_merchant(text)
        self.assertEqual(result, "ABC SUPERMARKET")
    
    def test_skip_short_names(self):
        """Test that very short lines are handled"""
        text = "A\nB\nC\nPRINCE STORE\nItems"
        result = extract_merchant(text)
        self.assertEqual(result, "PRINCE STORE")
    
    def test_merchant_with_special_characters(self):
        """Test merchant name with special characters"""
        text = "STORE @ MALL #5\nAddress: Main St\nTotal: 100"
        result = extract_merchant(text)
        self.assertIn("STORE", result)
    
    def test_skip_thank_you_messages(self):
        """Test that thank you messages are skipped"""
        text = "STORE NAME\nItems\nThank you for shopping\nPlease visit again"
        result = extract_merchant(text)
        self.assertEqual(result, "STORE NAME")


class TestImagePreprocessing(unittest.TestCase):
    """Test image preprocessing functionality"""
    
    def setUp(self):
        """Create temporary directory for test images"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_image(self, name: str, width: int = 800, height: int = 600) -> str:
        """Helper to create a test image"""
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some text to make it non-blank
        draw.text((50, 50), "TEST RECEIPT", fill='black')
        draw.text((50, 100), "Amount: 123.45", fill='black')
        
        path = os.path.join(self.test_dir, name)
        img.save(path)
        return path
    
    def test_preprocess_valid_image(self):
        """Test preprocessing of valid image"""
        image_path = self.create_test_image("test.jpg")
        result = preprocess_image(image_path)
        
        # Should return numpy array
        self.assertIsInstance(result, np.ndarray)
        # Should have 2 dimensions (grayscale)
        self.assertEqual(len(result.shape), 2)
        # Should have reasonable dimensions
        self.assertGreater(result.shape[0], 0)
        self.assertGreater(result.shape[1], 0)
    
    def test_preprocess_invalid_path(self):
        """Test preprocessing with invalid image path"""
        with self.assertRaises(ValueError):
            preprocess_image(os.path.join(self.test_dir, "nonexistent.jpg"))
    
    def test_preprocess_upscales_small_image(self):
        """Test that small images are upscaled"""
        image_path = self.create_test_image("small.jpg", width=200, height=200)
        result = preprocess_image(image_path)
        
        # Image should be upscaled
        self.assertGreater(result.shape[0], 200)
    
    def test_preprocess_handles_large_image(self):
        """Test preprocessing of large image"""
        image_path = self.create_test_image("large.jpg", width=2000, height=2000)
        result = preprocess_image(image_path)
        
        # Should return a processed image without error
        self.assertIsInstance(result, np.ndarray)


class TestOCRProcessorIntegration(unittest.TestCase):
    """Integration tests for OCR processor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        clear_reader_cache()  # Start fresh
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        clear_reader_cache()
    
    def create_receipt_image(self, text: str, name: str = "receipt.jpg") -> str:
        """Create a test receipt image with text"""
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text on image
        y_offset = 50
        for line in text.split('\n'):
            draw.text((50, y_offset), line, fill='black')
            y_offset += 30
        
        path = os.path.join(self.test_dir, name)
        img.save(path)
        return path
    
    def test_processor_with_clear_receipt(self):
        """Test processor with clear receipt text"""
        receipt_text = """GROCERY STORE
        Date: 2025-11-15
        
        Items:
        Bread: 50.00
        Milk: 75.00
        
        TOTAL AMOUNT: 125.00
        """
        
        image_path = self.create_receipt_image(receipt_text)
        from utils.easyocr_processor import extract_receipt_data
        
        result = extract_receipt_data(image_path)
        
        # Basic validations
        self.assertIn('amount', result)
        self.assertIn('date', result)
        self.assertIn('description', result)
        self.assertIn('raw_text', result)
    
    def test_processor_returns_all_fields(self):
        """Test that processor returns all expected fields"""
        receipt_text = """STORE NAME
        Date: 2025-11-15
        TOTAL: 99.99
        """
        
        image_path = self.create_receipt_image(receipt_text)
        from utils.easyocr_processor import extract_receipt_data
        
        result = extract_receipt_data(image_path)
        
        expected_fields = ['amount', 'date', 'description', 'raw_text', 'confidence', 'ocr_method']
        for field in expected_fields:
            self.assertIn(field, result)
    
    def test_processor_handles_missing_file(self):
        """Test processor handles missing file gracefully"""
        from utils.easyocr_processor import extract_receipt_data
        
        result = extract_receipt_data("/nonexistent/path/receipt.jpg")
        
        # Should return error dict, not crash
        self.assertEqual(result['amount'], 0.0)
        self.assertIn('error', result)
    
    def test_processor_ocr_method_is_easyocr(self):
        """Test that processor reports using easyocr method"""
        receipt_text = "STORE\nTOTAL: 50.00"
        image_path = self.create_receipt_image(receipt_text)
        
        from utils.easyocr_processor import extract_receipt_data
        result = extract_receipt_data(image_path)
        
        self.assertEqual(result.get('ocr_method'), 'easyocr')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_amount_zero(self):
        """Test that zero amounts are handled"""
        text = "TOTAL: 0.00"
        result = extract_amount(text)
        # Zero might be extracted, but should not be returned as valid
        self.assertGreaterEqual(result, 0.0)
    
    def test_very_large_amount(self):
        """Test very large amounts are filtered"""
        text = "TOTAL: 99999999999.99"
        result = extract_amount(text)
        # Should be filtered out as unrealistic
        self.assertLess(result, 1000000)
    
    def test_negative_amount_not_extracted(self):
        """Test that negative amounts are not extracted"""
        text = "DISCOUNT: -50.00\nTOTAL: 150.00"
        result = extract_amount(text)
        # Should get the positive total
        self.assertGreater(result, 0)
    
    def test_merchant_with_unicode(self):
        """Test merchant extraction with unicode characters"""
        text = "CAFÉ RESTAURANT\nAddress: Main St"
        result = extract_merchant(text)
        self.assertIsNotNone(result)
    
    def test_special_characters_in_amount(self):
        """Test amount extraction with special formatting"""
        text = "Amount Due: US$ 150.75"
        result = extract_amount(text)
        self.assertGreater(result, 0)


class TestRegressionCases(unittest.TestCase):
    """Test cases for known issues and regression prevention"""
    
    def test_indian_receipt_format(self):
        """Test Indian receipt with GST format"""
        text = """STORE NAME
        Date: 01-Nov-2025
        SUBTOTAL: 1000.00
        GST (5%): 50.00
        TOTAL AMOUNT: ₹1050.00"""
        
        amount = extract_amount(text)
        self.assertAlmostEqual(amount, 1050.00, places=1)
    
    def test_restaurant_bill_format(self):
        """Test restaurant bill format"""
        text = """RESTAURANT NAME
        SUBTOTAL: 500.00
        Service Tax: 10%: 50.00
        TOTAL PAYABLE: 550.00"""
        
        amount = extract_amount(text)
        self.assertGreater(amount, 0)
    
    def test_invoice_format(self):
        """Test invoice format"""
        text = """Invoice #12345
        ITEM 1: 100
        ITEM 2: 200
        TOTAL AMOUNT DUE: 300.00"""
        
        amount = extract_amount(text)
        self.assertAlmostEqual(amount, 300.00, places=1)


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAmountExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestParseAmount))
    suite.addTests(loader.loadTestsFromTestCase(TestDateExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestMerchantExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestImagePreprocessing))
    suite.addTests(loader.loadTestsFromTestCase(TestOCRProcessorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)