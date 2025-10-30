import pytesseract
from PIL import Image
import re
from datetime import datetime
import os

# Try to configure tesseract path for Windows
def configure_tesseract():
    # Common Tesseract paths on Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
        r'C:\ProgramData\chocolatey\bin\tesseract.exe'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True
    return False

def extract_receipt_data(image_path):
    """
    Extract receipt data from an image file using OCR.
    
    Args:
        image_path (str): Path to the receipt image file
        
    Returns:
        dict: Dictionary containing extracted receipt data with keys:
              - 'amount': Extracted transaction amount (float)
              - 'date': Extracted transaction date (string)
              - 'description': Merchant/store name (string)
              - 'raw_text': Full OCR text (string)
    """
    try:
        # Try to configure tesseract path
        tesseract_configured = configure_tesseract()
        
        if not tesseract_configured:
            print("Warning: Tesseract OCR not found. OCR functionality will be limited.")
            print("Please install Tesseract-OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
            # Return empty data with flag so the app doesn't crash
            return {
                'amount': 0.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Manual Entry Required (OCR not available)',
                'raw_text': '',
                'warning': 'Tesseract OCR not installed'
            }
        
        # Open and process image
        print(f"Processing receipt image: {image_path}")
        img = Image.open(image_path)
        
        # Improve OCR accuracy with image preprocessing
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        text = pytesseract.image_to_string(img)
        
        if not text or text.strip() == '':
            print("Warning: No text extracted from image. Image might be blank or unreadable.")
            return {
                'amount': 0.0,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'No text found in receipt image',
                'raw_text': text,
                'warning': 'No text extracted'
            }
        
        print(f"Extracted text length: {len(text)} characters")
        
        amount = extract_amount(text)
        date = extract_date(text)
        merchant = extract_merchant(text)

        print(f"Extracted - Amount: {amount}, Date: {date}, Merchant: {merchant}")
        
        return {
            'amount': amount,
            'date': date,
            'description': merchant or 'Receipt Purchase',
            'raw_text': text
        }
        
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return {
            'amount': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Error: Receipt file not found',
            'raw_text': '',
            'error': 'File not found'
        }
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return fallback data instead of None to prevent app crashes
        return {
            'amount': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': f'Error processing receipt: {type(e).__name__}',
            'raw_text': '',
            'error': str(e)
        }

def extract_amount(text):
    patterns = [
        r'(?:TOTAL|GRAND\s*TOTAL)[:\s]*\$?([0-9,]+\.?[0-9]*)',
        r'(?:Amount|AMOUNT|TOTAL\s*AMOUNT)[:\s]*\$?([0-9,]+\.?[0-9]*)',
        r'(?:PRICE|FINAL|DUE)[:\s]*\$?([0-9,]+\.?[0-9]*)',
        r'(?:SUBTOTAL|SUB\s*TOTAL)[:\s]*\$?([0-9,]+\.?[0-9]*)',
        r'\$\s*([0-9,]+\.[0-9]{2})',  # $XXX.XX format
        r'₹\s*([0-9,]+\.?[0-9]*)',  # Indian Rupee format
        r'([0-9]{1,5}[.,][0-9]{2})(?:\s|$)',  # Amount at end of line
        r'(?:^|\s)([0-9,]+\.[0-9]{2})(?:\s|$)',  # Decimal format with boundaries
        r'([0-9,]+\.?[0-9]{2})',  # Generic currency format
    ]

    largest_amount = 0.0
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            amount_str = match.group(1)
            
            # Determine if comma or dot is used as decimal separator
            # Count occurrences of both
            comma_count = amount_str.count(',')
            dot_count = amount_str.count('.')
            
            # Handle different decimal separators
            if comma_count > 0 and dot_count > 0:
                # Both exist - last one is decimal separator
                if amount_str.rfind(',') > amount_str.rfind('.'):
                    amount_str = amount_str.replace('.', '').replace(',', '.')
                else:
                    amount_str = amount_str.replace(',', '')
            elif comma_count > 1:
                # Multiple commas - they're thousands separators
                amount_str = amount_str.replace(',', '')
            elif comma_count == 1 and dot_count == 0:
                # Single comma, no dot - likely decimal separator
                amount_str = amount_str.replace(',', '.')
            else:
                # Default: remove all commas
                amount_str = amount_str.replace(',', '')
            
            try:
                amount = float(amount_str)
                # Filter out unreasonable amounts (typically > 99999) and too small
                if 0 < amount < 100000 and amount > largest_amount:
                    largest_amount = amount
            except ValueError:
                continue
    
    return largest_amount

def extract_date(text):
    date_patterns = [
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD-MM-YYYY or MM/DD/YYYY
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',  # Month DD, YYYY
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',  # DD Month YYYY
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                # Try to parse various date formats
                from dateutil import parser
                parsed_date = parser.parse(date_str)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                return date_str
    return datetime.now().strftime('%Y-%m-%d')

def extract_merchant(text):
    """Extract merchant/store name from receipt text"""
    if not text or not text.strip():
        return 'Receipt Purchase'
    
    lines = text.strip().split('\n')
    
    # Common receipt keywords to skip
    skip_keywords = [
        'TOTAL', 'AMOUNT', 'TAX', 'SUBTOTAL', 'PRICE', 'ITEM', 'QTY',
        'THANK', 'WELCOME', 'INVOICE', 'RECEIPT', 'ORDER', 'REF', 'PHONE',
        'ADDRESS', 'PAID', 'CHANGE', 'CASH', 'CARD', 'THANK YOU', 'PLEASE'
    ]
    
    candidates = []
    
    for i, line in enumerate(lines[:15]):  # Check first 15 lines
        line = line.strip()
        
        # Skip empty lines and very short lines
        if len(line) < 3 or len(line) > 100:
            continue
        
        # Skip lines that are purely numeric
        if re.search(r'^\d+$', line):
            continue
        
        # Skip lines with too many numbers (likely amounts or codes)
        digit_ratio = len(re.findall(r'\d', line)) / len(line)
        if digit_ratio > 0.6:
            continue
        
        # Skip known receipt labels
        if any(keyword in line.upper() for keyword in skip_keywords):
            continue
        
        # Skip lines with special characters only
        if re.search(r'^[^\w\s]*$', line):
            continue
        
        # Prioritize first meaningful line (usually the merchant)
        candidates.append((i, line))
    
    # Return first candidate or default
    if candidates:
        return candidates[0][1]
    
    return 'Receipt Purchase'
